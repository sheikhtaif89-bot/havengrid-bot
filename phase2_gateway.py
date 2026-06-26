#!/usr/bin/env python3
import sys
import logging
import sqlite3
import requests
import numpy as np
import json
import os
import time
import asyncio
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Importing from your project structure
try:
    from performance_tracker import get_success_rate
except ImportError:
    # Fallback if file is missing
    def get_success_rate():
        return 0.6

# --- CONFIGURATION ---
DB_PATH      = "havengrid_server.db"
SYMBOLS      = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
ROLLING_DAYS = 90
TELEGRAM_BOT_TOKEN = "8974817423:AAFmplYVPFfAQ4OSnex7x3YfH6fwSZqSZHw"
TELEGRAM_CHAT_ID   = "6237287904"
UTC_TZ             = pytz.UTC

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("HavengridGateway")

# --- ADAPTIVE LOGIC ---
def get_adaptive_thresholds():
    success_rate = get_success_rate()
    if success_rate < 0.5:
        return 25, 75 
    else:
        return 35, 65 

# --- SIGNAL PERSISTENCE ---
def save_signal_to_file(asset, signal_type, price, sl, tp):
    signal_entry = {
        "id": int(time.time()),
        "asset": asset,
        "type": signal_type,
        "price": round(price, 2),
        "sl": round(sl, 2),
        "tp": round(tp, 2)
    }
    try:
        signals = []
        if os.path.exists("signals.json"):
            with open("signals.json", "r") as f:
                try: signals = json.load(f)
                except: signals = []
        signals.append(signal_entry)
        if len(signals) > 50: signals = signals[-50:]
        with open("signals.json", "w") as f:
            json.dump(signals, f, indent=4)
        logger.info(f"Signal saved for {asset}")
    except Exception as e:
        logger.error(f"Failed to save signal: {e}")

# --- TELEGRAM ENGINE ---
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: 
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Telegram alert failed: {e}")

# --- STRATEGY ENGINE ---
def get_closes_array(symbol, timeframe, limit=60):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT close_avg FROM aggregated_ohlcv WHERE symbol=? AND timeframe=? ORDER BY ts ASC LIMIT ?", (symbol, timeframe, limit))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_structural_sr(symbol):
    cutoff_ts = int((datetime.now(UTC_TZ) - timedelta(days=ROLLING_DAYS)).timestamp() * 1000)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(low_avg), MAX(high_avg) FROM aggregated_ohlcv WHERE symbol=? AND timeframe='1h' AND ts>=?", (symbol, cutoff_ts))
    row = cursor.fetchone()
    conn.close()
    return (float(row[0]), float(row[1])) if row and row[0] else None

def compute_rsi_14(prices):
    if len(prices) < 15: return None
    deltas = np.diff(prices)
    up, down = deltas[deltas >= 0].sum() / 14, -deltas[deltas < 0].sum() / 14
    rs = up / down if down != 0 else 999
    return 100 - (100 / (1 + rs))

def evaluate_confluence_matrix():
    logger.info("Evaluating market confluence...")
    rsi_lower, rsi_upper = get_adaptive_thresholds()
    for symbol in SYMBOLS:
        sr = get_structural_sr(symbol)
        if not sr: continue
        support, resistance = sr
        closes_15m = get_closes_array(symbol, "15m", 100)
        if len(closes_15m) < 15: continue
        rsi_val = compute_rsi_14(closes_15m)
        latest_price = closes_15m[-1]
        
        if latest_price <= (support * 1.01) and rsi_val < rsi_lower:
            save_signal_to_file(symbol, "BUY", latest_price, support*0.99, support*1.05)
            send_telegram_alert(f"🔥 BUY Signal: {symbol} at {latest_price:.2f}")
        elif latest_price >= (resistance * 0.99) and rsi_val > rsi_upper:
            save_signal_to_file(symbol, "SELL", latest_price, resistance*1.01, resistance*0.95)
            send_telegram_alert(f"⚠️ SELL Signal: {symbol} at {latest_price:.2f}")

async def main_async():
    scheduler = AsyncIOScheduler(timezone=UTC_TZ)
    scheduler.add_job(evaluate_confluence_matrix, trigger="cron", minute="1,16,31,46")
    evaluate_confluence_matrix() # Run immediately on start
    scheduler.start()
    while True:
        await asyncio.sleep(60)

def main():
    try:
        asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Phase 2 terminated.")

if __name__ == "__main__":
    main()