import json
import os

def track_trade(signal_id, result):
    history_file = "trade_history.json"
    history = []
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            try: history = json.load(f)
            except: history = []
    history.append({"id": signal_id, "result": result})
    with open(history_file, "w") as f:
        json.dump(history, f)

def get_success_rate():
    if not os.path.exists("trade_history.json"): return 0.5
    with open("trade_history.json", "r") as f:
        try: history = json.load(f)
        except: return 0.5
    if not history: return 0.5
    wins = sum(1 for t in history if t['result'] == 1)
    return wins / len(history)