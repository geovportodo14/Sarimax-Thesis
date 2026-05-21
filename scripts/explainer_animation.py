"""Generate an animated explainer GIF for the SARIMAX Energy Dashboard.

Audience: senior high school (research colloquium).
Output: reports/sarimax_explainer.gif

Run:
    python3 scripts/explainer_animation.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "reports" / "sarimax_explainer.gif"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

FPS = 12
W_IN, H_IN, DPI = 10.0, 5.625, 110  # ~1100x620

# Real numbers from backend/forecasting/outputs/2026-03-02/_recommendation.json
PREDICTED_PHP = 49.18
OPTIMIZED_PHP = 41.56
SAVINGS_PHP = round(PREDICTED_PHP - OPTIMIZED_PHP, 2)
BUDGET_PHP = 200.00
TARIFF_PHP_KWH = 9.775   # from optimized_schedule.csv (Meralco March 2026)
SAVINGS_MONTH = round(SAVINGS_PHP * 30, 0)
SAVINGS_YEAR = round(SAVINGS_PHP * 365, 0)
APPLIANCE_BREAKDOWN = {
    "Refrigerator": 25.86,
    "Aircon": 14.59,
    "Electric Fan": 8.73,
}

# Palette
BG = "#0F172A"        # slate-900
PANEL = "#1E293B"     # slate-800
TEXT = "#F8FAFC"      # slate-50
MUTED = "#94A3B8"     # slate-400
ACCENT = "#FBBF24"    # amber-400 (energy)
DATA = "#38BDF8"      # sky-400
GOOD = "#34D399"      # emerald-400
BAD = "#F87171"       # red-400

# Scene durations (seconds) — total 120s for a 2-minute ad
SCENES = [
    ("cold_open",         10.0),
    ("intro",              8.0),
    ("problem",           10.0),
    ("audience",           8.0),
    ("data",              10.0),
    ("cloud",              8.0),
    ("sarimax_explained", 14.0),
    ("forecast",          12.0),
    ("budget",             8.0),
    ("optimize",          12.0),
    ("results",           12.0),
    ("outro",              8.0),
]
TOTAL_SECS = sum(d for _, d in SCENES)
TOTAL_FRAMES = int(TOTAL_SECS * FPS)


def scene_at(t: float):
    """Return (scene_name, local_time, scene_duration) for global time t."""
    elapsed = 0.0
    for name, dur in SCENES:
        if t < elapsed + dur:
            return name, t - elapsed, dur
        elapsed += dur
    name, dur = SCENES[-1]
    return name, dur, dur


def ease(t: float) -> float:
    """Smooth easing 0..1 -> 0..1 (ease-in-out)."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def fade(local_t: float, dur: float, fade_in: float = 0.4, fade_out: float = 0.4) -> float:
    """Compute opacity 0..1 with fade in/out within a scene."""
    if local_t < fade_in:
        return ease(local_t / fade_in)
    if local_t > dur - fade_out:
        return ease((dur - local_t) / fade_out)
    return 1.0


# ---------------------------------------------------------------------------
# Figure setup
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_axis_off()


def clear():
    ax.clear()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.set_facecolor(BG)


def panel(x, y, w, h, color=PANEL, alpha=1.0, radius=2.0):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        linewidth=0, facecolor=color, alpha=alpha,
    )
    ax.add_patch(rect)


def appliance_icon(cx, cy, kind: str, scale: float = 1.0, alpha: float = 1.0):
    """Draw a simple stylized appliance icon."""
    s = scale
    if kind == "aircon":
        body = patches.FancyBboxPatch(
            (cx - 6*s, cy - 2*s), 12*s, 4*s,
            boxstyle=f"round,pad=0.0,rounding_size={0.8*s}",
            facecolor="#60A5FA", edgecolor="white", linewidth=1.2, alpha=alpha,
        )
        ax.add_patch(body)
        for i in range(3):
            ax.plot([cx - 4*s + i*4*s, cx - 4*s + i*4*s],
                    [cy - 1.2*s, cy + 1.2*s],
                    color="white", lw=1.0, alpha=alpha)
        ax.text(cx, cy - 4*s, "AC", ha="center", va="top",
                color=TEXT, fontsize=9, alpha=alpha, weight="bold")
    elif kind == "fridge":
        body = patches.FancyBboxPatch(
            (cx - 3*s, cy - 5*s), 6*s, 10*s,
            boxstyle=f"round,pad=0.0,rounding_size={0.6*s}",
            facecolor="#A7F3D0", edgecolor="white", linewidth=1.2, alpha=alpha,
        )
        ax.add_patch(body)
        ax.plot([cx - 3*s, cx + 3*s], [cy + 1.5*s, cy + 1.5*s],
                color="white", lw=1.2, alpha=alpha)
        ax.plot([cx + 1.8*s, cx + 1.8*s], [cy + 2.5*s, cy + 3.5*s],
                color="#0F172A", lw=1.6, alpha=alpha)
        ax.plot([cx + 1.8*s, cx + 1.8*s], [cy - 0.5*s, cy + 0.5*s],
                color="#0F172A", lw=1.6, alpha=alpha)
        ax.text(cx, cy - 7*s, "Fridge", ha="center", va="top",
                color=TEXT, fontsize=9, alpha=alpha, weight="bold")
    elif kind == "fan":
        circ = patches.Circle((cx, cy), 4*s, facecolor="#FCD34D",
                              edgecolor="white", lw=1.2, alpha=alpha)
        ax.add_patch(circ)
        for ang in (0, 60, 120, 180, 240, 300):
            r = np.deg2rad(ang)
            ax.plot([cx, cx + 3.2*s*np.cos(r)],
                    [cy, cy + 3.2*s*np.sin(r)],
                    color="white", lw=1.6, alpha=alpha)
        ax.add_patch(patches.Circle((cx, cy), 0.6*s,
                     facecolor="white", alpha=alpha))
        ax.text(cx, cy - 6*s, "Fan", ha="center", va="top",
                color=TEXT, fontsize=9, alpha=alpha, weight="bold")


def cloud_icon(cx, cy, scale: float = 1.0, alpha: float = 1.0, color="#38BDF8"):
    s = scale
    for dx, dy, r in [(-3*s, 0, 2.4*s), (0, 1.2*s, 3.0*s),
                      (3*s, 0, 2.4*s), (0, -0.6*s, 2.0*s)]:
        ax.add_patch(patches.Circle((cx+dx, cy+dy), r,
                     facecolor=color, alpha=alpha, edgecolor="none"))
    ax.add_patch(patches.Rectangle(
        (cx-4*s, cy-1.4*s), 8*s, 1.6*s,
        facecolor=color, alpha=alpha, edgecolor="none"))


# ---------------------------------------------------------------------------
# Pre-compute SARIMAX-like demo series
# ---------------------------------------------------------------------------
np.random.seed(7)
HIST_HOURS = 48
FCST_HOURS = 24
hours_h = np.arange(HIST_HOURS)
hours_f = np.arange(HIST_HOURS, HIST_HOURS + FCST_HOURS)
daily = 0.6 + 0.5 * np.sin((hours_h % 24) / 24 * 2 * np.pi - np.pi / 2)
noise = np.random.normal(0, 0.08, HIST_HOURS)
hist = np.clip(daily + noise, 0.05, None)
daily_f = 0.6 + 0.5 * np.sin((hours_f % 24) / 24 * 2 * np.pi - np.pi / 2)
fcst = np.clip(daily_f + np.random.normal(0, 0.04, FCST_HOURS), 0.05, None)
ci = 0.18 * np.ones_like(fcst)


# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------
def draw_cold_open(t: float, dur: float):
    a = fade(t, dur, 0.6, 0.5)

    # Top hook text — bilingual to land with PH high-school audience
    ax.text(50, 78, "Hindi mo alam kung magkano ang kuryente mo...",
            ha="center", color=TEXT, fontsize=16, weight="bold", alpha=a)
    if t > 2.0:
        a2 = ease(min(1.0, (t - 2.0) / 0.8)) * a
        ax.text(50, 70, "...hanggang dumating ang bill.",
                ha="center", color=BAD, fontsize=16,
                weight="bold", alpha=a2, style="italic")

    # Animated peso counter ticking up — feels like the bill is rising
    progress = ease(min(1.0, t / (dur * 0.75)))
    rolling = int(progress * 4287)  # land on a plausible monthly bill
    ax.add_patch(patches.FancyBboxPatch(
        (28, 28), 44, 24,
        boxstyle="round,pad=0,rounding_size=2",
        facecolor="#FEF3C7", edgecolor=BAD, lw=2.2, alpha=a))
    ax.text(50, 46, "ELECTRIC BILL", ha="center",
            color=BAD, fontsize=10, weight="bold", alpha=a)
    ax.text(50, 36, f"₱ {rolling:,}", ha="center",
            color="#0F172A", fontsize=28, weight="bold", alpha=a)

    if t > 6.5:
        a3 = ease(min(1.0, (t - 6.5) / 1.2)) * a
        ax.text(50, 14,
                "What if you could see it coming?",
                ha="center", color=ACCENT, fontsize=13,
                weight="bold", alpha=a3, style="italic")


def draw_intro(t: float, dur: float):
    a = fade(t, dur, 0.6, 0.4)
    # Subtle pulsing accent ring
    pulse = 0.5 + 0.5 * np.sin(t * 2.0)
    ax.add_patch(patches.Circle((50, 55), 22 + pulse * 1.5,
                 facecolor="none", edgecolor=ACCENT, lw=1.4, alpha=0.4 * a))
    # Lightning bolt
    bolt = np.array([[48, 70], [54, 70], [50, 60], [56, 60], [46, 45], [50, 55], [44, 55]])
    ax.add_patch(patches.Polygon(bolt, closed=True, facecolor=ACCENT,
                 edgecolor="white", lw=1.2, alpha=a))

    ax.text(50, 32, "SARIMAX Energy Dashboard",
            ha="center", va="center", color=TEXT,
            fontsize=22, weight="bold", alpha=a)
    ax.text(50, 24, "Predict your electricity bill — before it arrives.",
            ha="center", va="center", color=MUTED,
            fontsize=12, alpha=a)
    ax.text(50, 12, "Research Colloquium  •  Senior High School Presentation",
            ha="center", va="center", color=ACCENT,
            fontsize=9, alpha=0.8 * a, style="italic")


def draw_problem(t: float, dur: float):
    a = fade(t, dur, 0.4, 0.4)
    ax.text(50, 90, "The Problem",
            ha="center", color=BAD, fontsize=11, weight="bold", alpha=a)
    ax.text(50, 83,
            "We only see the electricity bill at the END of the month.",
            ha="center", color=TEXT, fontsize=13, alpha=a)

    # House outline
    house = np.array([[30, 30], [70, 30], [70, 55], [50, 70], [30, 55], [30, 30]])
    ax.add_patch(patches.Polygon(house, closed=True,
                 facecolor=PANEL, edgecolor=TEXT, lw=1.4, alpha=a))
    # Door
    ax.add_patch(patches.Rectangle((47, 30), 6, 12,
                 facecolor=BG, edgecolor=TEXT, lw=1.0, alpha=a))

    # Appliances pop in one by one
    if t > 0.6:
        appliance_icon(38, 48, "aircon", scale=0.7, alpha=a)
    if t > 1.2:
        appliance_icon(50, 50, "fridge", scale=0.6, alpha=a)
    if t > 1.8:
        appliance_icon(62, 48, "fan", scale=0.6, alpha=a)

    # Meter dial spinning + bill jumping
    if t > 2.0:
        cx, cy, r = 85, 55, 6
        ax.add_patch(patches.Circle((cx, cy), r, facecolor=PANEL,
                     edgecolor=TEXT, lw=1.2, alpha=a))
        ang = (t - 2.0) * 360 * 4  # fast spin
        rad = np.deg2rad(ang - 90)
        ax.plot([cx, cx + 4.5 * np.cos(rad)], [cy, cy + 4.5 * np.sin(rad)],
                color=BAD, lw=2.2, alpha=a)
        ax.text(cx, cy - 9, "meter", ha="center", color=MUTED,
                fontsize=8, alpha=a)

    # Shocked bill
    if t > 2.6:
        b_a = ease((t - 2.6) / 1.0) * a
        ax.add_patch(patches.FancyBboxPatch(
            (8, 14), 22, 14,
            boxstyle="round,pad=0,rounding_size=1.2",
            facecolor="#FEF3C7", edgecolor=BAD, lw=1.8, alpha=b_a))
        ax.text(19, 24, "ELECTRIC BILL", ha="center", color=BAD,
                fontsize=8.5, weight="bold", alpha=b_a)
        ax.text(19, 18.5, "₱ ???", ha="center", color="#0F172A",
                fontsize=16, weight="bold", alpha=b_a)


def draw_data(t: float, dur: float):
    a = fade(t, dur, 0.4, 0.4)
    ax.text(50, 90, "Step 1 — Smart Plugs Collect Data",
            ha="center", color=DATA, fontsize=11, weight="bold", alpha=a)
    ax.text(50, 83, "Every appliance is metered every 10 minutes.",
            ha="center", color=TEXT, fontsize=12, alpha=a)

    # 3 appliances on the left
    appliance_icon(18, 60, "aircon", scale=0.7, alpha=a)
    appliance_icon(18, 42, "fridge", scale=0.6, alpha=a)
    appliance_icon(18, 24, "fan", scale=0.6, alpha=a)

    # Cloud on the right
    cloud_icon(82, 48, scale=1.6, alpha=a)
    ax.text(82, 36, "Cloud Database", ha="center", color=TEXT,
            fontsize=10, weight="bold", alpha=a)

    # Flying data dots
    n_dots = 24
    for i in range(n_dots):
        phase = ((t * 0.55) + i / n_dots) % 1.0
        y_row = [60, 42, 24][i % 3]
        x = 25 + phase * 50
        size = 14 + 6 * np.sin(phase * np.pi)
        ax.scatter([x], [y_row + np.sin(phase * np.pi * 2) * 1.5],
                   s=size, color=DATA, alpha=a * (0.4 + 0.6 * (1 - abs(phase - 0.5) * 2)))

    # Counter ticking up
    target = 86_400
    progress = ease(min(1.0, t / (dur * 0.85)))
    val = int(progress * target)
    ax.text(50, 12, f"Data points collected:  {val:,}",
            ha="center", color=ACCENT, fontsize=12, weight="bold", alpha=a)


def draw_forecast(t: float, dur: float):
    a = fade(t, dur, 0.4, 0.5)
    ax.text(50, 92, "Step 4 — SARIMAX Learns the Pattern",
            ha="center", color=ACCENT, fontsize=11, weight="bold", alpha=a)
    ax.text(50, 86, "It studies past usage to predict the next 24 hours.",
            ha="center", color=TEXT, fontsize=11, alpha=a)

    # Inner chart area (data coords 0..100)
    x0, y0, x1, y1 = 12, 22, 92, 76
    panel(x0, y0, x1 - x0, y1 - y0, color=PANEL, alpha=0.65 * a, radius=2)

    # Axes ticks (just baseline)
    ax.plot([x0 + 2, x1 - 2], [y0 + 3, y0 + 3], color=MUTED, lw=0.8, alpha=a)
    ax.plot([x0 + 6, x0 + 6], [y0 + 3, y1 - 3], color=MUTED, lw=0.8, alpha=a)

    # Map data to chart coords
    span_x = (x1 - 4) - (x0 + 6)
    total_hours = HIST_HOURS + FCST_HOURS
    sx = lambda h: x0 + 6 + (h / total_hours) * span_x
    ymin, ymax = 0.0, max(hist.max(), fcst.max()) * 1.3
    sy = lambda v: y0 + 4 + (v - ymin) / (ymax - ymin) * (y1 - y0 - 7)

    # Draw historical progressively
    reveal_t = ease(min(1.0, t / (dur * 0.55)))
    hi = int(reveal_t * HIST_HOURS)
    if hi > 1:
        xs = [sx(h) for h in hours_h[:hi]]
        ys = [sy(v) for v in hist[:hi]]
        ax.plot(xs, ys, color=DATA, lw=2.0, alpha=a)
        ax.scatter([xs[-1]], [ys[-1]], s=24, color=DATA,
                   edgecolor="white", lw=0.8, alpha=a, zorder=5)

    # Vertical "now" line once history is done
    if reveal_t >= 1.0:
        nx = sx(HIST_HOURS - 1)
        ax.plot([nx, nx], [y0 + 3, y1 - 3], color=MUTED,
                lw=1.0, linestyle=":", alpha=0.8 * a)
        ax.text(nx, y1 - 1.5, "now", ha="center", color=MUTED,
                fontsize=8, alpha=a)

    # Forecast reveal in second half
    fcst_t = ease(max(0.0, min(1.0, (t / dur - 0.55) / 0.40)))
    fi = int(fcst_t * FCST_HOURS)
    if fi > 1:
        xs_f = [sx(h) for h in hours_f[:fi]]
        ys_f = [sy(v) for v in fcst[:fi]]
        # Confidence band
        upper = [sy(v + c) for v, c in zip(fcst[:fi], ci[:fi])]
        lower = [sy(max(0, v - c)) for v, c in zip(fcst[:fi], ci[:fi])]
        ax.fill_between(xs_f, lower, upper, color=ACCENT,
                        alpha=0.18 * a, linewidth=0)
        ax.plot(xs_f, ys_f, color=ACCENT, lw=2.0,
                linestyle="--", alpha=a, dash_capstyle="round")
        ax.scatter([xs_f[-1]], [ys_f[-1]], s=28, color=ACCENT,
                   edgecolor="white", lw=0.8, alpha=a, zorder=5)

    # Legend
    ax.plot([15, 19], [27, 27], color=DATA, lw=2.2, alpha=a)
    ax.text(20, 27, "history (actual usage)", color=TEXT,
            fontsize=9, va="center", alpha=a)
    ax.plot([46, 50], [27, 27], color=ACCENT, lw=2.2,
            linestyle="--", alpha=a)
    ax.text(51, 27, "forecast (next 24 h)", color=TEXT,
            fontsize=9, va="center", alpha=a)


def draw_optimize(t: float, dur: float):
    a = fade(t, dur, 0.4, 0.4)
    ax.text(50, 92, "Step 6 — Optimize the Schedule",
            ha="center", color=GOOD, fontsize=11, weight="bold", alpha=a)
    ax.text(50, 86, "Shift flexible appliances away from peak tariff hours.",
            ha="center", color=TEXT, fontsize=11, alpha=a)

    # Tariff curve (background) - simple peak shape
    hours_arr = np.arange(24)
    tariff = 1 + 0.7 * np.exp(-((hours_arr - 19) ** 2) / 18)  # peak around 7pm
    bx0, bx1 = 10, 90
    by0, by1 = 30, 70
    sx = lambda h: bx0 + (h / 23) * (bx1 - bx0)
    sy = lambda v: by0 + (v - 0.9) / 0.9 * (by1 - by0)

    panel(bx0 - 2, by0 - 4, bx1 - bx0 + 4, by1 - by0 + 14,
          color=PANEL, alpha=0.6 * a, radius=2)

    # Draw tariff curve
    xs = [sx(h) for h in hours_arr]
    ys = [sy(v) for v in tariff]
    ax.plot(xs, ys, color=BAD, lw=1.2, alpha=0.65 * a)
    ax.fill_between(xs, [by0 - 3] * 24, ys, color=BAD,
                    alpha=0.10 * a, linewidth=0)
    ax.text(sx(19), by1 + 3, "peak hours",
            ha="center", color=BAD, fontsize=9, alpha=a)

    # "Before" usage bars (concentrated around peak)
    # First half: show baseline; second half: animate shift to off-peak
    shift = ease(max(0.0, min(1.0, (t / dur - 0.30) / 0.55)))
    bar_w = (bx1 - bx0) / 28
    for h in hours_arr:
        # baseline weight
        base_w = np.exp(-((h - 19) ** 2) / 8)
        # shifted weight (push to off-peak 22-6)
        if h in (0, 1, 2, 3, 4, 5, 22, 23):
            shifted_w = 0.9
        else:
            shifted_w = 0.15
        w = base_w * (1 - shift) + shifted_w * shift
        bar_h = 1 + w * 14
        ax.add_patch(patches.Rectangle(
            (sx(h) - bar_w / 2, by0 - 2), bar_w * 0.9, bar_h,
            facecolor=DATA, alpha=0.85 * a, edgecolor="none"))

    ax.text(sx(0), by0 - 5.5, "12 AM", ha="center", color=MUTED,
            fontsize=8, alpha=a)
    ax.text(sx(12), by0 - 5.5, "12 PM", ha="center", color=MUTED,
            fontsize=8, alpha=a)
    ax.text(sx(23), by0 - 5.5, "11 PM", ha="center", color=MUTED,
            fontsize=8, alpha=a)

    # Before / After cost panels appear after shift completes-ish
    reveal = ease(max(0.0, min(1.0, (t / dur - 0.55) / 0.40)))
    panel(8, 12, 30, 12, color="#7F1D1D", alpha=0.35 * a * reveal, radius=1.5)
    ax.text(10, 19, "Before optimization", color=BAD,
            fontsize=9, alpha=a * reveal, weight="bold")
    ax.text(10, 14, f"₱ {PREDICTED_PHP:.2f}", color=TEXT,
            fontsize=15, weight="bold", alpha=a * reveal)

    # arrow
    if reveal > 0.2:
        ax.annotate("", xy=(60, 18), xytext=(40, 18),
                    arrowprops=dict(arrowstyle="-|>",
                                    color=ACCENT, lw=2.0,
                                    alpha=a * reveal))

    panel(62, 12, 30, 12, color="#064E3B", alpha=0.35 * a * reveal, radius=1.5)
    ax.text(64, 19, "After optimization", color=GOOD,
            fontsize=9, alpha=a * reveal, weight="bold")
    ax.text(64, 14, f"₱ {OPTIMIZED_PHP:.2f}", color=TEXT,
            fontsize=15, weight="bold", alpha=a * reveal)
    ax.text(88, 14, f"−₱{SAVINGS_PHP:.2f}", color=GOOD,
            fontsize=10, weight="bold", alpha=a * reveal, ha="right")


def draw_audience(t: float, dur: float):
    a = fade(t, dur, 0.4, 0.4)
    ax.text(50, 90, "Why does it matter?",
            ha="center", color=ACCENT, fontsize=11, weight="bold", alpha=a)
    ax.text(50, 83,
            "Electricity is one of the biggest monthly expenses of every Filipino home.",
            ha="center", color=TEXT, fontsize=12, alpha=a)

    # Three info tiles slide in with stagger
    tiles = [
        ("Families",   "Pay ₱2,000–5,000\nevery month",       DATA),
        ("Students",   "Worry about\nbaon vs. bills",         ACCENT),
        ("The Planet", "Less waste =\ngreener future",        GOOD),
    ]
    x = 10
    for i, (title, body, color) in enumerate(tiles):
        delay = 0.4 + i * 0.7
        if t < delay:
            x += 28
            continue
        ai = ease(min(1.0, (t - delay) / 0.6)) * a
        offset = (1 - ease(min(1.0, (t - delay) / 0.6))) * 4
        panel(x, 30 - offset, 26, 36, color=PANEL,
              alpha=0.85 * ai, radius=2)
        # color stripe at top of the tile
        ax.add_patch(patches.Rectangle((x, 65.2 - offset), 26, 0.8,
                     facecolor=color, alpha=ai, edgecolor="none"))
        ax.text(x + 13, 58 - offset, title, ha="center",
                color=color, fontsize=13, weight="bold", alpha=ai)
        ax.text(x + 13, 46 - offset, body, ha="center",
                color=TEXT, fontsize=10, alpha=ai)
        x += 28

    if t > dur - 1.4:
        ai = ease(min(1.0, (t - (dur - 1.4)) / 0.6)) * a
        ax.text(50, 16,
                "Our goal: give every household this knowledge — before the bill.",
                ha="center", color=MUTED, fontsize=10,
                alpha=ai, style="italic")


def draw_cloud(t: float, dur: float):
    a = fade(t, dur, 0.4, 0.4)
    ax.text(50, 90, "Step 2 — Data Flows to the Cloud",
            ha="center", color=DATA, fontsize=11, weight="bold", alpha=a)
    ax.text(50, 83,
            "Every reading is saved securely on a cloud database.",
            ha="center", color=TEXT, fontsize=11, alpha=a)

    # Big cloud center stage
    cloud_icon(50, 55, scale=2.6, alpha=a, color="#38BDF8")
    ax.text(50, 47, "MongoDB Atlas", ha="center",
            color=TEXT, fontsize=10, weight="bold", alpha=a)

    # Streams falling INTO the cloud from above
    for i in range(20):
        phase = ((t * 0.7) + i / 20) % 1.0
        y = 90 - phase * 35
        x = 30 + (i % 5) * 10
        ax.scatter([x], [y], s=14, color=DATA,
                   alpha=a * (1 - phase) * 0.9)

    # Three stat tiles below
    stats = [
        ("90+", "days of history"),
        ("10,000+", "data points / appliance"),
        ("24/7", "live collection"),
    ]
    if t > 1.5:
        ai = ease(min(1.0, (t - 1.5) / 0.8)) * a
        x = 8
        for value, label in stats:
            panel(x, 8, 28, 18, color=PANEL, alpha=0.85 * ai, radius=2)
            ax.text(x + 14, 19, value, ha="center", color=ACCENT,
                    fontsize=14, weight="bold", alpha=ai)
            ax.text(x + 14, 12, label, ha="center", color=MUTED,
                    fontsize=9, alpha=ai)
            x += 30


def draw_sarimax_explained(t: float, dur: float):
    a = fade(t, dur, 0.4, 0.4)
    ax.text(50, 92, "Step 3 — What is SARIMAX?",
            ha="center", color=ACCENT, fontsize=11,
            weight="bold", alpha=a)
    ax.text(50, 86,
            "A statistical model that learns patterns in time series data.",
            ha="center", color=TEXT, fontsize=11, alpha=a)

    # The 7 letters reveal one at a time
    letters = [
        ("S", "Seasonal",   "day & night patterns"),
        ("AR", "AutoRegressive", "uses its own past"),
        ("I", "Integrated", "handles trends"),
        ("MA", "Moving Average", "smooths noise"),
        ("X", "eXogenous", "uses weather too"),
    ]
    cols = len(letters)
    col_w = 88 / cols
    for i, (letter, name, sub) in enumerate(letters):
        delay = 0.6 + i * 1.4
        if t < delay:
            continue
        ai = ease(min(1.0, (t - delay) / 0.6)) * a
        cx = 6 + col_w * (i + 0.5)
        cy = 56
        # Big letter circle
        ax.add_patch(patches.Circle((cx, cy), 5.5,
                     facecolor=ACCENT, edgecolor="white",
                     lw=1.4, alpha=ai))
        ax.text(cx, cy - 0.6, letter, ha="center", va="center",
                color="#0F172A", fontsize=14, weight="bold", alpha=ai)
        ax.text(cx, cy - 10, name, ha="center",
                color=TEXT, fontsize=10, weight="bold", alpha=ai)
        ax.text(cx, cy - 15, sub, ha="center",
                color=MUTED, fontsize=8.5, alpha=ai)

    # Bottom plain-English summary
    if t > dur - 4.0:
        ai = ease(min(1.0, (t - (dur - 4.0)) / 0.8)) * a
        panel(8, 16, 84, 12, color=PANEL, alpha=0.85 * ai, radius=2)
        ax.text(50, 24,
                "In plain English:",
                ha="center", color=MUTED, fontsize=10, alpha=ai)
        ax.text(50, 19,
                "SARIMAX learns from your past usage + weather to predict the future.",
                ha="center", color=TEXT, fontsize=11,
                weight="bold", alpha=ai)


def draw_budget(t: float, dur: float):
    a = fade(t, dur, 0.4, 0.4)
    ax.text(50, 90, "Step 5 — Set Your Daily Budget",
            ha="center", color=GOOD, fontsize=11,
            weight="bold", alpha=a)
    ax.text(50, 83,
            "Tell the system how much you can spend per day.",
            ha="center", color=TEXT, fontsize=11, alpha=a)

    # Budget bar — slider style
    bx, by, bw, bh = 14, 56, 72, 10
    panel(bx, by, bw, bh, color=PANEL, alpha=0.9 * a, radius=2)
    util = PREDICTED_PHP / BUDGET_PHP   # 0.246
    fill_w = bw * util
    ax.add_patch(patches.FancyBboxPatch(
        (bx, by), fill_w, bh,
        boxstyle="round,pad=0,rounding_size=2",
        facecolor=GOOD, alpha=0.9 * a, edgecolor="none"))
    ax.text(bx, by + bh + 2, "₱0", color=MUTED, fontsize=9, alpha=a)
    ax.text(bx + bw, by + bh + 2, f"₱{BUDGET_PHP:.0f}",
            color=MUTED, fontsize=9, alpha=a, ha="right")

    # Caret + prediction label
    ax.annotate("", xy=(bx + fill_w, by - 1),
                xytext=(bx + fill_w, by - 5),
                arrowprops=dict(arrowstyle="-|>", color=ACCENT,
                                lw=1.6, alpha=a))
    ax.text(bx + fill_w, by - 7,
            f"Predicted today: ₱{PREDICTED_PHP:.2f}",
            ha="center", color=ACCENT, fontsize=10,
            weight="bold", alpha=a)

    # Two outcome cards
    if t > 2.5:
        ai = ease(min(1.0, (t - 2.5) / 0.8)) * a
        panel(10, 18, 38, 22, color="#064E3B", alpha=0.35 * ai, radius=2)
        ax.text(29, 33, "✓  Within budget",
                ha="center", color=GOOD, fontsize=11,
                weight="bold", alpha=ai)
        ax.text(29, 25,
                "Enjoy your day.",
                ha="center", color=TEXT, fontsize=10, alpha=ai)

        panel(52, 18, 38, 22, color="#7F1D1D", alpha=0.35 * ai, radius=2)
        ax.text(71, 33, "!  Over budget",
                ha="center", color=BAD, fontsize=11,
                weight="bold", alpha=ai)
        ax.text(71, 25,
                "Get alerted by email — early.",
                ha="center", color=TEXT, fontsize=10, alpha=ai)


def draw_results(t: float, dur: float):
    a = fade(t, dur, 0.4, 0.5)
    ax.text(50, 92, "Real Savings, Every Day",
            ha="center", color=GOOD, fontsize=12, weight="bold", alpha=a)
    ax.text(50, 86,
            f"Based on Meralco rate ₱{TARIFF_PHP_KWH:.3f}/kWh "
            "and your real appliance data.",
            ha="center", color=MUTED, fontsize=10, alpha=a)

    # Three escalating savings tiles
    tiles = [
        ("Per day",    f"₱{SAVINGS_PHP:.2f}",  DATA),
        ("Per month",  f"₱{SAVINGS_MONTH:.0f}", ACCENT),
        ("Per year",   f"₱{SAVINGS_YEAR:.0f}",  GOOD),
    ]
    for i, (label, val, color) in enumerate(tiles):
        delay = 0.6 + i * 1.0
        if t < delay:
            continue
        ai = ease(min(1.0, (t - delay) / 0.7)) * a
        offset_y = (1 - ease(min(1.0, (t - delay) / 0.7))) * 4
        x = 6 + i * 31
        panel(x, 50 - offset_y, 28, 26, color=PANEL,
              alpha=0.9 * ai, radius=2)
        ax.add_patch(patches.Rectangle((x, 76 - offset_y), 28, 0.8,
                     facecolor=color, alpha=ai, edgecolor="none"))
        ax.text(x + 14, 65 - offset_y, val, ha="center", color=color,
                fontsize=18, weight="bold", alpha=ai)
        ax.text(x + 14, 56 - offset_y, label, ha="center",
                color=MUTED, fontsize=10, alpha=ai)

    if t > dur - 4.0:
        ai = ease(min(1.0, (t - (dur - 4.0)) / 0.8)) * a
        ax.text(50, 36,
                f"That's about {int(SAVINGS_YEAR // 60)} jeepney rides a year — saved.",
                ha="center", color=TEXT, fontsize=12,
                weight="bold", alpha=ai)
    if t > dur - 2.6:
        ai = ease(min(1.0, (t - (dur - 2.6)) / 0.8)) * a
        ax.text(50, 14,
                "Note: Meralco rates change monthly. "
                "Projections may differ from your actual bill.",
                ha="center", color=MUTED, fontsize=8.5,
                alpha=ai, style="italic")


def draw_outro(t: float, dur: float):
    a = fade(t, dur, 0.5, 0.6)

    # Pulsing lightning bolt
    pulse = 0.5 + 0.5 * np.sin(t * 2.0)
    ax.add_patch(patches.Circle((50, 70), 9 + pulse * 1.0,
                 facecolor="none", edgecolor=ACCENT,
                 lw=1.4, alpha=0.4 * a))
    bolt = np.array([[49, 76], [53, 76], [50.5, 71], [55, 71],
                     [47, 62], [50, 69], [45, 69]])
    ax.add_patch(patches.Polygon(bolt, closed=True, facecolor=ACCENT,
                 edgecolor="white", lw=1.2, alpha=a))

    ax.text(50, 50, "Smarter Energy. Lower Bills.",
            ha="center", color=TEXT, fontsize=20,
            weight="bold", alpha=a)
    ax.text(50, 42, "A greener future starts with knowing.",
            ha="center", color=MUTED, fontsize=11, alpha=a)

    ax.text(50, 28, "SARIMAX Energy Dashboard",
            ha="center", color=ACCENT, fontsize=13,
            weight="bold", alpha=a)
    ax.text(50, 22,
            "by Geovanny Porto Do  •  Senior High School Research Colloquium",
            ha="center", color=MUTED, fontsize=9.5,
            alpha=a, style="italic")
    ax.text(50, 12, "Thank you!", ha="center", color=TEXT,
            fontsize=14, alpha=a, weight="bold")


SCENE_FUNCS = {
    "cold_open":         draw_cold_open,
    "intro":             draw_intro,
    "problem":           draw_problem,
    "audience":          draw_audience,
    "data":              draw_data,
    "cloud":             draw_cloud,
    "sarimax_explained": draw_sarimax_explained,
    "forecast":          draw_forecast,
    "budget":            draw_budget,
    "optimize":          draw_optimize,
    "results":           draw_results,
    "outro":             draw_outro,
}


def render(frame_idx: int):
    t = frame_idx / FPS
    name, local_t, dur = scene_at(t)
    clear()

    # Subtle top-right scene counter / progress bar at bottom
    SCENE_FUNCS[name](local_t, dur)

    # Bottom progress bar
    prog = t / TOTAL_SECS
    ax.add_patch(patches.Rectangle((0, 0), 100, 0.8,
                 facecolor="#1E293B", edgecolor="none"))
    ax.add_patch(patches.Rectangle((0, 0), 100 * prog, 0.8,
                 facecolor=ACCENT, edgecolor="none"))
    return []


def main():
    print(f"Rendering {TOTAL_FRAMES} frames at {FPS} fps "
          f"({TOTAL_SECS:.1f}s) -> {OUT_PATH}")
    anim = FuncAnimation(fig, render, frames=TOTAL_FRAMES,
                         interval=1000 / FPS, blit=False)
    writer = PillowWriter(fps=FPS)
    anim.save(OUT_PATH, writer=writer, dpi=DPI)
    size_mb = OUT_PATH.stat().st_size / (1024 * 1024)
    print(f"Done. {OUT_PATH}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
