import threading
import logging
import time
import importlib

logging.basicConfig(filename='bot_errors.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

PHASES = [
    "phase1_ingest",
    "phase2_gateway",
    "phase3_notifications",
    "phase4_rbac",
    "phase5_ui",
    "phase6_dashboard"
]

def run_phase(module_name):
    while True:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, 'main'):
                module.main()
            else:
                break
        except Exception as e:
            logging.error(f"CRASH in {module_name}: {e}")
            time.sleep(5)

if __name__ == "__main__":
    for phase in PHASES:
        thread = threading.Thread(target=run_phase, args=(phase,), daemon=True)
        thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass