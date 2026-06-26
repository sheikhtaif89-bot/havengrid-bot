import threading
impo
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
