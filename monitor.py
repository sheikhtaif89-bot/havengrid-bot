import time
from data_collector.worker import fetch_and_update, init_db, prune_old_data
import requests

TOKEN = "8974817423:AAFmplYVPFfAQ4OSnex7x3YfH6fwSZqSZHw"
CHAT_ID = "6237287904"
SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except: 
        pass

init_db()
counter = 0

print("Monitoring system started...")

while True:
    for s in SYMBOLS:
        price, vol = fetch_and_update(s)
        if vol and vol > 500000000: 
            send_msg(f"🔥 HIGH ALERT: {s} Price: {price} | Vol: {vol}")
        elif price:
            print(f"Updated {s}: {price}")

    send_msg("📊 Market Status Update: Monitoring 24/7.")
    
    counter += 1
    # Check every 24 hours (288 cycles * 5 minutes = 1440 minutes)
    if counter >= 288:
        prune_old_data()
        counter = 0
        
    time.sleep(300) # 5-minute interval