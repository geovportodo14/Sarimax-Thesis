import sys
import os
import tensorflow as tf
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from TimeGan import build_timegan, train_embedder_step, train_supervisor_step, train_joint_step

def verify_training_steps():
    print("STAGE 3: Verifying Training Steps...")
    
    # Setup
    seq_len = 24
    x_dim = 3
    h_dim = 10
    units = 16
    heads = 2
    lr = 0.001
    z_dim = 16
    batch_size = 4
    
    model = build_timegan(seq_len, x_dim, h_dim, units, heads, lr)
    
    # Dummy Batch
    x_batch = tf.random.normal((batch_size, seq_len, x_dim))
    
    try:
        # 1. Embedder Step
        loss_e = train_embedder_step(model, x_batch)
        print(f" - Embedder Step Loss: {loss_e:.4f} (OK)")
        
        # 2. Supervisor Step
        loss_s = train_supervisor_step(model, x_batch)
        print(f" - Supervisor Step Loss: {loss_s:.4f} (OK)")
        
        # 3. Joint Step
        g_loss, e_loss, d_loss = train_joint_step(
            model, x_batch, z_dim=z_dim, gamma=1.0, lambda_sup=1.0, lambda_rec=1.0
        )
        print(f" - Joint Step Losses: G={g_loss:.4f}, E={e_loss:.4f}, D={d_loss:.4f} (OK)")
        
        print("STAGE 3: Training Steps Verification PASSED!")
        return True
        
    except Exception as e:
        print(f"STAGE 3 FAILED with error: {e}")
        return False

if __name__ == "__main__":
    verify_training_steps()
