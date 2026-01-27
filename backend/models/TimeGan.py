import argparse
import os
import math
import warnings
from dataclasses import dataclass
from typing import Optional, Tuple, List

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

import tensorflow as tf
from tensorflow.keras import layers, Model

warnings.filterwarnings("ignore")


# -----------------------------
# Helpers
# -----------------------------
def parse_value_to_float(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str):
        s = x.strip()
        if s.lower() == "true":
            return 1.0
        if s.lower() == "false":
            return 0.0
        try:
            return float(s)
        except Exception:
            return np.nan
    try:
        return float(x)
    except Exception:
        return np.nan


def long_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert long IoT log:
      timestamp | device | property | value
    into wide numeric features:
      index=timestamp, columns like Device__property
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

    if not {"device", "property", "value"}.issubset(df.columns):
        raise ValueError("CSV must contain: timestamp, device, property, value")

    df["key"] = df["device"].astype(str) + "__" + df["property"].astype(str)
    df["value_num"] = df["value"].apply(parse_value_to_float)

    wide = (
        df.pivot_table(index="timestamp", columns="key", values="value_num", aggfunc="last")
        .sort_index()
    )

    return wide


def find_best_column(columns: List[str], keywords: List[str]) -> Optional[str]:
    """
    Pick the first column that matches any keyword (case-insensitive),
    prioritizing closer matches.
    """
    cols = list(columns)
    lower = [c.lower() for c in cols]

    # exact keyword containment
    for kw in keywords:
        kw = kw.lower()
        for c, cl in zip(cols, lower):
            if kw in cl:
                return c
    return None


def resample_fixed(wide: pd.DataFrame, freq: str) -> pd.DataFrame:
    # Mean works for continuous measurements; you can change per-column if needed
    out = wide.resample(freq).mean()
    # Fill gaps typical in event logs
    out = out.ffill().bfill()
    out = out.fillna(0.0)
    return out


def build_daily_sequences(X: np.ndarray, seq_len: int) -> np.ndarray:
    """
    X: (T, F) at fixed freq
    returns daily chunks aligned to midnight: (N_days, seq_len, F)
    """
    if X.shape[0] < seq_len:
        raise ValueError("Not enough points to form even one daily sequence.")

    n_days = X.shape[0] // seq_len
    X = X[: n_days * seq_len]
    return X.reshape(n_days, seq_len, X.shape[1]).astype(np.float32)


def compute_kwh_total(power_w: np.ndarray, freq_minutes: int, start_kwh: float = 0.0) -> np.ndarray:
    """
    power_w: (T,) power in W
    kWh increment per step = (W/1000) * (freq_minutes/60)
    """
    delta_h = freq_minutes / 60.0
    inc = (power_w / 1000.0) * delta_h
    return start_kwh + np.cumsum(inc)


# -----------------------------
# Improved TimeGAN building blocks
# -----------------------------
class GRUWithMHSA(layers.Layer):
    def __init__(self, units: int, heads: int, **kwargs):
        super().__init__(**kwargs)
        self.gru = layers.GRU(units, return_sequences=True)
        # key_dim should be >=1
        key_dim = max(1, units // max(1, heads))
        self.mhsa = layers.MultiHeadAttention(num_heads=heads, key_dim=key_dim)
        self.ln = layers.LayerNormalization()
        self.proj = layers.Dense(units, activation="relu")

    def call(self, x, training=False):
        h = self.gru(x, training=training)
        attn = self.mhsa(query=h, value=h, key=h, training=training)
        h2 = self.ln(h + attn)
        return self.proj(h2)


def make_embedding(seq_len: int, x_dim: int, h_dim: int, units: int) -> Model:
    x_in = layers.Input(shape=(seq_len, x_dim))
    h = layers.LSTM(units, return_sequences=True)(x_in)
    h = layers.Dense(h_dim, activation="sigmoid")(h)
    return Model(x_in, h, name="Embedding")


def make_recovery(seq_len: int, h_dim: int, x_dim: int, units: int, heads: int) -> Model:
    h_in = layers.Input(shape=(seq_len, h_dim))
    y = GRUWithMHSA(units=units, heads=heads)(h_in)
    x_hat = layers.Dense(x_dim, activation="sigmoid")(y)
    return Model(h_in, x_hat, name="Recovery")


def make_generator(seq_len: int, z_dim: int, h_dim: int, units: int) -> Model:
    z_in = layers.Input(shape=(seq_len, z_dim))
    g = layers.GRU(units, return_sequences=True)(z_in)
    h_hat = layers.Dense(h_dim, activation="sigmoid")(g)
    return Model(z_in, h_hat, name="Generator")


def make_supervisor(seq_len: int, h_dim: int, units: int) -> Model:
    h_in = layers.Input(shape=(seq_len, h_dim))
    s = layers.GRU(units, return_sequences=True)(h_in)
    h_sup = layers.Dense(h_dim, activation="sigmoid")(s)
    return Model(h_in, h_sup, name="Supervisor")


def make_discriminator(seq_len: int, h_dim: int, units: int) -> Model:
    h_in = layers.Input(shape=(seq_len, h_dim))
    d = layers.GRU(units, return_sequences=True)(h_in)
    y = layers.Dense(1)(d)  # logits per timestep
    return Model(h_in, y, name="Discriminator")


@dataclass
class TimeGAN:
    embedding: Model
    recovery: Model
    generator: Model
    supervisor: Model
    discriminator: Model
    e_opt: tf.keras.optimizers.Optimizer
    g_opt: tf.keras.optimizers.Optimizer
    d_opt: tf.keras.optimizers.Optimizer


def bce_logits(y_true, y_logit):
    return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=y_true, logits=y_logit))


@tf.function
def train_embedder_step(model: TimeGAN, x):
    with tf.GradientTape() as tape:
        h = model.embedding(x, training=True)
        x_tilde = model.recovery(h, training=True)
        loss_e = tf.reduce_mean(tf.square(x - x_tilde))
    vars_e = model.embedding.trainable_variables + model.recovery.trainable_variables
    grads = tape.gradient(loss_e, vars_e)
    model.e_opt.apply_gradients(zip(grads, vars_e))
    return loss_e


@tf.function
def train_supervisor_step(model: TimeGAN, x):
    with tf.GradientTape() as tape:
        h = model.embedding(x, training=True)
        h_sup = model.supervisor(h, training=True)
        loss_s = tf.reduce_mean(tf.square(h[:, 1:, :] - h_sup[:, :-1, :]))
    grads = tape.gradient(loss_s, model.supervisor.trainable_variables)
    model.g_opt.apply_gradients(zip(grads, model.supervisor.trainable_variables))
    return loss_s


@tf.function
def train_joint_step(model: TimeGAN, x, z_dim: int, gamma: float, lambda_sup: float, lambda_rec: float):
    batch = tf.shape(x)[0]
    seq_len = tf.shape(x)[1]
    z = tf.random.normal(shape=(batch, seq_len, z_dim))

    # 1) Generator + supervisor
    with tf.GradientTape() as tape_g:
        h_real = model.embedding(x, training=True)
        h_fake = model.generator(z, training=True)
        h_fake_sup = model.supervisor(h_fake, training=True)

        y_fake = model.discriminator(h_fake_sup, training=True)
        g_loss_u = bce_logits(tf.ones_like(y_fake), y_fake)

        h_real_sup = model.supervisor(h_real, training=True)
        g_loss_s = tf.reduce_mean(tf.square(h_real[:, 1:, :] - h_real_sup[:, :-1, :]))

        x_fake = model.recovery(h_fake_sup, training=True)
        x_mean, x_var = tf.nn.moments(x, axes=[0, 1])
        xf_mean, xf_var = tf.nn.moments(x_fake, axes=[0, 1])
        g_loss_m = tf.reduce_mean(tf.abs(x_mean - xf_mean)) + tf.reduce_mean(
            tf.abs(tf.sqrt(x_var + 1e-6) - tf.sqrt(xf_var + 1e-6))
        )

        g_loss = gamma * g_loss_u + lambda_sup * g_loss_s + g_loss_m

    g_vars = model.generator.trainable_variables + model.supervisor.trainable_variables
    g_grads = tape_g.gradient(g_loss, g_vars)
    model.g_opt.apply_gradients(zip(g_grads, g_vars))

    # 2) Embedder + recovery
    with tf.GradientTape() as tape_e:
        h = model.embedding(x, training=True)
        x_tilde = model.recovery(h, training=True)
        h_sup = model.supervisor(h, training=True)

        e_loss_rec = tf.reduce_mean(tf.square(x - x_tilde))
        e_loss_sup = tf.reduce_mean(tf.square(h[:, 1:, :] - h_sup[:, :-1, :]))
        e_loss = lambda_rec * e_loss_rec + 0.1 * e_loss_sup

    e_vars = model.embedding.trainable_variables + model.recovery.trainable_variables
    e_grads = tape_e.gradient(e_loss, e_vars)
    model.e_opt.apply_gradients(zip(e_grads, e_vars))

    # 3) Discriminator
    with tf.GradientTape() as tape_d:
        h_real = model.embedding(x, training=False)
        y_real = model.discriminator(h_real, training=True)

        h_fake = model.generator(z, training=False)
        h_fake_sup = model.supervisor(h_fake, training=False)
        y_fake = model.discriminator(h_fake_sup, training=True)

        d_loss = bce_logits(tf.ones_like(y_real), y_real) + bce_logits(tf.zeros_like(y_fake), y_fake)

    d_grads = tape_d.gradient(d_loss, model.discriminator.trainable_variables)
    model.d_opt.apply_gradients(zip(d_grads, model.discriminator.trainable_variables))

    return g_loss, e_loss, d_loss


def build_timegan(seq_len: int, x_dim: int, h_dim: int, units: int, heads: int, lr: float) -> TimeGAN:
    embedding = make_embedding(seq_len, x_dim, h_dim, units)
    recovery = make_recovery(seq_len, h_dim, x_dim, units, heads)
    generator = make_generator(seq_len, z_dim=16, h_dim=h_dim, units=units)
    supervisor = make_supervisor(seq_len, h_dim, units)
    discriminator = make_discriminator(seq_len, h_dim, units)

    opt_e = tf.keras.optimizers.Adam(learning_rate=lr)
    opt_g = tf.keras.optimizers.Adam(learning_rate=lr)
    opt_d = tf.keras.optimizers.Adam(learning_rate=lr)

    return TimeGAN(embedding, recovery, generator, supervisor, discriminator, opt_e, opt_g, opt_d)


# -----------------------------
# Main pipeline
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="/mnt/data/energy_log_20260109.csv")
    parser.add_argument("--output", type=str, default="synthetic_table316_2025.csv")

    # Training basis window (your request)
    parser.add_argument("--train-start", type=str, default="2026-01-03")
    parser.add_argument("--train-end", type=str, default="2026-03-03")

    # Output generation window (set whatever you want)
    parser.add_argument("--gen-start", type=str, default="2025-01-01 00:00:00")
    parser.add_argument("--gen-end", type=str, default="2025-12-31 23:50:00")

    parser.add_argument("--freq", type=str, default="10min")
    parser.add_argument("--seq-len", type=int, default=144)

    # Optional: explicitly choose which pivoted columns to use
    parser.add_argument("--voltage-col", type=str, default=None)
    parser.add_argument("--current-col", type=str, default=None)
    parser.add_argument("--power-col", type=str, default=None)

    # Model hyperparams (paper-style defaults)
    parser.add_argument("--units", type=int, default=64)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--h-dim", type=int, default=24)
    parser.add_argument("--z-dim", type=int, default=16)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--batch", type=int, default=128)
    parser.add_argument("--epochs", type=int, default=800)

    # Loss weights
    parser.add_argument("--gamma", type=float, default=1.0)
    parser.add_argument("--lambda-sup", type=float, default=100.0)
    parser.add_argument("--lambda-rec", type=float, default=1.0)

    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    np.random.seed(args.seed)
    tf.random.set_seed(args.seed)

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input not found: {args.input}")

    # Load + wide pivot
    df = pd.read_csv(args.input)
    wide = long_to_wide(df)

    # Filter to training window
    train_start = pd.Timestamp(args.train_start)
    train_end = pd.Timestamp(args.train_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    wide_train = wide.loc[(wide.index >= train_start) & (wide.index <= train_end)].copy()
    if wide_train.empty:
        raise ValueError(
            f"No data found in training range {args.train_start} to {args.train_end}. "
            "If your file doesn't cover these dates yet, adjust --train-start/--train-end."
        )

    # Resample
    wide_train = resample_fixed(wide_train, args.freq)

    # Auto-detect V/I/P columns if not provided
    vol_col = args.voltage_col or find_best_column(wide_train.columns, ["volt", "voltage", "v_rms", "vrms"])
    cur_col = args.current_col or find_best_column(wide_train.columns, ["curr", "current", "amps", "ampere"])
    pwr_col = args.power_col or find_best_column(wide_train.columns, ["power", "watt", "active_power", "pwr"])

    if not (vol_col and cur_col and pwr_col):
        # Show user what columns exist so they can pick
        sample_cols = ", ".join(list(wide_train.columns)[:40])
        raise ValueError(
            "Could not auto-detect Voltage/Current/Power columns from pivoted features.\n"
            f"Detected: voltage={vol_col}, current={cur_col}, power={pwr_col}\n\n"
            "Fix: pass explicit names:\n"
            "  --voltage-col '<Device__property>' --current-col '<Device__property>' --power-col '<Device__property>'\n\n"
            f"Example available columns (first 40): {sample_cols}"
        )

    data_train = wide_train[[vol_col, cur_col, pwr_col]].copy()
    data_train.columns = ["Voltage (V)", "Current (A)", "Power (W)"]

    # Align to full days (midnight anchored) and build daily sequences
    # We enforce exact seq_len points per day by trimming to multiples of seq_len.
    X = data_train.values.astype(np.float32)
    X_days = build_daily_sequences(X, seq_len=args.seq_len)  # (N_days, 144, 3)

    # Scale to [0,1]
    scaler = MinMaxScaler(feature_range=(0, 1))
    flat = X_days.reshape(-1, X_days.shape[-1])
    scaler.fit(flat)
    Xn = scaler.transform(flat).reshape(X_days.shape).astype(np.float32)

    # TF dataset
    ds = tf.data.Dataset.from_tensor_slices(Xn).shuffle(len(Xn), seed=args.seed, reshuffle_each_iteration=True)
    ds = ds.batch(args.batch, drop_remainder=True).prefetch(tf.data.AUTOTUNE)

    # Build model
    model = build_timegan(
        seq_len=args.seq_len,
        x_dim=3,
        h_dim=args.h_dim,
        units=args.units,
        heads=args.heads,
        lr=args.lr
    )

    # -------------------------
    # Train (3 phases)
    # -------------------------
    # Phase 1: embedder/recovery pretrain
    for epoch in range(1, args.epochs + 1):
        e_losses = []
        for xb in ds:
            e_losses.append(float(train_embedder_step(model, xb)))
        if epoch % 50 == 0 or epoch == 1:
            print(f"[Phase1][{epoch}/{args.epochs}] Recon loss: {np.mean(e_losses):.6f}")

    # Phase 2: supervisor pretrain
    sup_epochs = max(1, args.epochs // 2)
    for epoch in range(1, sup_epochs + 1):
        s_losses = []
        for xb in ds:
            s_losses.append(float(train_supervisor_step(model, xb)))
        if epoch % 50 == 0 or epoch == 1:
            print(f"[Phase2][{epoch}/{sup_epochs}] Sup loss: {np.mean(s_losses):.6f}")

    # Phase 3: joint training
    for epoch in range(1, args.epochs + 1):
        gL, eL, dL = [], [], []
        for xb in ds:
            g_loss, e_loss, d_loss = train_joint_step(
                model, xb, z_dim=args.z_dim,
                gamma=args.gamma, lambda_sup=args.lambda_sup, lambda_rec=args.lambda_rec
            )
            gL.append(float(g_loss)); eL.append(float(e_loss)); dL.append(float(d_loss))
        if epoch % 50 == 0 or epoch == 1:
            print(f"[Phase3][{epoch}/{args.epochs}] G:{np.mean(gL):.4f} E:{np.mean(eL):.4f} D:{np.mean(dL):.4f}")

    # -------------------------
    # Generate synthetic period
    # -------------------------
    gen_index = pd.date_range(start=pd.Timestamp(args.gen_start), end=pd.Timestamp(args.gen_end), freq=args.freq)
    T = len(gen_index)
    seq_len = args.seq_len
    n_seq = math.ceil(T / seq_len)

    # sample
    z = tf.random.normal(shape=(n_seq, seq_len, args.z_dim))
    h_fake = model.generator(z, training=False)
    h_fake_sup = model.supervisor(h_fake, training=False)
    x_fake = model.recovery(h_fake_sup, training=False).numpy().astype(np.float32)  # (n_seq, seq_len, 3)

    x_fake = x_fake.reshape(-1, 3)[:T]

    # inverse scale back to physical units
    x_denorm = scaler.inverse_transform(x_fake)

    out = pd.DataFrame(x_denorm, index=gen_index, columns=["Voltage (V)", "Current (A)", "Power (W)"])

    # kWh Total computed from generated power (monotonic + consistent)
    # freq minutes from args.freq (assumes "10min" etc.)
    freq_minutes = int(pd.to_timedelta(args.freq).total_seconds() // 60)
    out["kWh Total"] = compute_kwh_total(out["Power (W)"].to_numpy(), freq_minutes=freq_minutes, start_kwh=0.0)

    # Format like Table 3.16
    out = out.reset_index().rename(columns={"index": "Timestamp"})

    # Optional rounding similar to your table
    out["Voltage (V)"] = out["Voltage (V)"].round(1)
    out["Current (A)"] = out["Current (A)"].round(2)
    out["Power (W)"] = out["Power (W)"].round(1)
    out["kWh Total"] = out["kWh Total"].round(3)

    out.to_csv(args.output, index=False)
    print(f"Saved: {args.output}  rows={len(out)}")
    print("Columns:", list(out.columns))
    print("\nSample (10 rows):")
    print(out.head(10).to_string(index=False))


if __name__ == "__main__":
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    main()
