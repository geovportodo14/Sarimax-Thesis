import sys
import os
import tensorflow as tf
import numpy as np

# Ensure backend folder is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from TimeGan import build_timegan

def verify_model_architecture():
    print("STAGE 2: Verifying Model Architecture...")
    
    # Dummy parameters
    seq_len = 24
    x_dim = 3
    h_dim = 10
    units = 16
    heads = 2
    lr = 0.001
    
    try:
        model = build_timegan(seq_len, x_dim, h_dim, units, heads, lr)
        
        # Check inputs and outputs of each component
        batch_size = 4
        
        # 1. Embedder
        x_dummy = tf.random.normal((batch_size, seq_len, x_dim))
        h_dummy = model.embedding(x_dummy)
        assert h_dummy.shape == (batch_size, seq_len, h_dim), f"Embedder output shape wrong: {h_dummy.shape}"
        print(" - Embedder: OK")
        
        # 2. Recovery
        x_rec = model.recovery(h_dummy)
        assert x_rec.shape == (batch_size, seq_len, x_dim), f"Recovery output shape wrong: {x_rec.shape}"
        print(" - Recovery: OK")
        
        # 3. Supervisor
        h_sup = model.supervisor(h_dummy)
        assert h_sup.shape == (batch_size, seq_len, h_dim), f"Supervisor output shape wrong: {h_sup.shape}"
        print(" - Supervisor: OK")
        
        # 4. Generator
        z_dummy = tf.random.normal((batch_size, seq_len, 16)) # z_dim assumed 16 in TimeGan.py make_generator
        h_gen = model.generator(z_dummy)
        assert h_gen.shape == (batch_size, seq_len, h_dim), f"Generator output shape wrong: {h_gen.shape}"
        print(" - Generator: OK")
        
        # 5. Discriminator
        y_disc = model.discriminator(h_dummy)
        assert y_disc.shape == (batch_size, seq_len, 1), f"Discriminator output shape wrong: {y_disc.shape}"
        print(" - Discriminator: OK")
        
        print("STAGE 2: Model Architecture Verification PASSED!")
        return True
        
    except Exception as e:
        print(f"STAGE 2 FAILED with error: {e}")
        return False

if __name__ == "__main__":
    verify_model_architecture()
