import subprocess
import time
import os

# Files to launch in order
files = [
    "phase1_ingest.py", 
    "phase2_gateway.py", 
    "phase3_notifications.py", 
    "phase4_rbac.py", 
    "monitor.py"
]

print("--- Havengrid System Master Launcher ---")
print("Starting all modules, please wait...")

processes = []

for f in files:
    if os.path.exists(f):
        # Start each module as a separate process
        p = subprocess.Popen(["python", f])
        processes.append(p)
        print(f"Successfully launched: {f}")
        time.sleep(2) 
    else:
        print(f"Error: {f} not found! Please check the file name.")

print("\nAll modules are running. Press Ctrl+C to stop the entire system.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping all modules...")
    for p in processes:
        p.terminate() 
    print("System stopped safely.")