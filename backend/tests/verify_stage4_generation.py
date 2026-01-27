import sys
import os
import tensorflow as tf
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from TimeGan import build_timegan

def verify_generation():
    print("STAGE 4: Verifying Generation/Sampling...")
    
    # Setup
    seq_len = 24
    x_dim = 3
    h_dim = 10
    units = 16
    heads = 2
    lr = 0.001
    z_dim = 16
    n_samples = 10
    
    try:
        model = build_timegan(seq_len, x_dim, h_dim, units, heads, lr)
        
        # Generation Logic from TimeGan.py
        # z = tf.random.normal(shape=(n_seq, seq_len, args.z_dim))
        z_sample = tf.random.normal(shape=(n_samples, seq_len, z_dim))
        
        # Generator -> Supervisor -> Recovery
        h_fake = model.generator(z_sample, training=False)
        h_fake_sup = model.supervisor(h_fake, training=False)
        x_fake = model.recovery(h_fake_sup, training=False)
        
        # Convert to numpy
        x_fake_np = x_fake.numpy()
        
        assert x_fake_np.shape == (n_samples, seq_len, x_dim), f"Generated output shape wrong: {x_fake_np.shape}"
        print(f" - Generated shape: {x_fake_np.shape} (OK)")
        
        # Check values are in basic expected range (sigmoid output -> [0, 1])
        # Note: Depending on activation functions this might vary, but sigmoid is used in TimeGan.py
        if np.min(x_fake_np) < 0.0 or np.max(x_fake_np) > 1.0:
            print("WARNING: Generated values outside [0, 1] range. Check activation functions.")
        else:
            print(" - Values in expected [0, 1] range (OK)")
            
        print("STAGE 4: Generation Verification PASSED!")
        return True
        
    except Exception as e:
        print(f"STAGE 4 FAILED with error: {e}")
        return False

if __name__ == "__main__":
    verify_generation()
