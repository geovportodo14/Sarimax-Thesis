import subprocess
import os
import time
import signal
import sys

def run_services():
    print("="*50)
    print("  SARIMAX THESIS - BACKEND ORCHESTRATOR")
    print("="*50)
    
    # Detect Python command
    python_cmd = "./venv/bin/python3" if os.path.exists("./venv/bin/python3") else "python3"
    
    processes = []
    
    try:
        # 1. Start API Service
        print("\n[1/2] Starting API Service (FastAPI)...")
        api_proc = subprocess.Popen(
            [python_cmd, "-m", "uvicorn", "backend.api.index:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        processes.append(api_proc)
        
        # 2. Start Data Collector Service
        print("[2/2] Starting Data Collector Service...")
        collector_proc = subprocess.Popen(
            [python_cmd, "backend/collector/data_collector.py"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        processes.append(collector_proc)
        
        print("\n" + "!"*50)
        print(" SUCCESS: All services are running!")
        print(" API: http://localhost:8000")
        print(" Collector: Running in background (polling every 10m)")
        print(" " + "!"*50)
        print("\nPress Ctrl+C to safely shut down all services.")
        
        # Keep the script alive
        while True:
            time.sleep(1)
            # Check if any process died
            if api_proc.poll() is not None:
                print("\nError: API service stopped unexpectedly.")
                break
            if collector_proc.poll() is not None:
                print("\nError: Collector service stopped unexpectedly.")
                break
                
    except KeyboardInterrupt:
        print("\n\nShutting down services gracefully...")
        for proc in processes:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("All processes stopped. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        for proc in processes:
            proc.kill()

if __name__ == "__main__":
    run_services()
