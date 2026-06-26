import asyncio
import sqlite3
import logging
import os
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from data_collector.worker import fetch_and_update, init_db as init_collector_db

# --- CONFIGURATION ---
DB_PATH = "havengrid_server.db"
TIMEZONE = "UTC"
SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
TIMEFRAMES = ["15m", "1h"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("Phase1Ingest")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aggregated_ohlcv (
            ts INTEGER,
            symbol TEXT,
            timeframe TEXT,
            open_avg REAL,
            high_avg REAL,
            low_avg REAL,
            close_avg REAL
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def fetch_and_store(symbol, timeframe):
    price, vol = fetch_and_update(symbol)
    if price:
        logger.info(f"Successfully synced {symbol} | Price: {price} | Vol: {vol}")
        
        # ডাটাবেসে ডাটা ইনসার্ট করার কোড
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO aggregated_ohlcv (ts, symbol, timeframe, open_avg, high_avg, low_avg, close_avg)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (int(time.time()), symbol, timeframe, price, price, price, price)) # এখানে আপনার লজিক অনুযায়ী ভ্যালু সেট করুন
        conn.commit()
        conn.close()
    else:
        logger.error(f"Failed to fetch {symbol}")

def prune_old_data():
    from data_collector.worker import prune_old_data as prune_collector
    prune_collector()
    logger.info("Old data pruned successfully.")

async def main_async():
    # Proxy cleanup
    for env_var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(env_var, None)

    init_db()
    init_collector_db() 
    
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    # Simplified job scheduling
    scheduler.add_job(lambda: [fetch_and_store(sym, "15m") for sym in SYMBOLS], trigger="cron", minute="*/15")
    scheduler.add_job(lambda: [fetch_and_store(sym, "1h") for sym in SYMBOLS], trigger="cron", minute=0)
    scheduler.add_job(prune_old_data, trigger="cron", hour=0, minute=0)

    logger.info("Starting baseline sync engine...")
    for sym in SYMBOLS:
        for tf in TIMEFRAMES:
            fetch_and_store(sym, tf)
    logger.info("Baseline data execution sync completed.")
    
    scheduler.start()
    logger.info("Havengrid Base Scheduler Thread actively listening.")

    while True:
        await asyncio.sleep(60)

def main():
    try:
        asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Phase 1 process terminated.")

if __name__ == "__main__":
    main()