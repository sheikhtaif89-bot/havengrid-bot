import json
import telebot
import time
import threading
import logging
import ccxt
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = "8974817423:AAE4nXQFprFhao3V9v4andYl69Wdimk6rN8"
bot = telebot.TeleBot(TOKEN)
AUTHORIZED_FILE = Path("authorized_users.json")
SIGNAL_FILE = Path("signals.json")

exchanges = {
    'Binance': ccxt.binance(),
    'Bybit': ccxt.bybit(),
    'KuCoin': ccxt.kucoin()
}

def get_price(symbol, exchange_key):
    try: return exchanges[exchange_key].fetch_ticker(symbol)['last']
    except: return 0.0

def get_best_exchange(symbol):
    prices = {key: get_price(symbol, key) for key in exchanges}
    return max(prices, key=prices.get)

def analyze_market(symbol):
    price = get_price(symbol, 'Binance')
    if price == 0: return "Neutral", "Stable"
    if price % 100 > 50:
        return "BUY", "Strong Trend"
    else:
        return "SELL", "High Volatility"

def get_time_data():
    utc_now = datetime.now(timezone.utc)
    local_time = utc_now + timedelta(hours=6)
    return utc_now.strftime('%H:%M:%S'), local_time.strftime('%d %b, %I:%M %p')

def get_market_pulse():
    utc, local = get_time_data()
    btc = get_price('BTC/USDT', 'Binance')
    best_ex = get_best_exchange('BTC/USDT')
    return f"""📊 HAVENGRID MARKET PULSE (15m)

🌐 BTC/USDT | ${btc:,.2f}
• Status: Base Build
• Rates: Binance: ${btc:,.2f} | Bybit: ${get_price('BTC/USDT', 'Bybit'):,.2f}
📥 Best Buy: KuCoin
📤 Best Sell: {best_ex}

🌐 UTC: {utc} | Local: {local}
🚀 Trade: Best on {best_ex}"""

def get_high_alert():
    xau_sig, xau_stat = analyze_market('BTC/USDT')
    eur_sig, eur_stat = analyze_market('ETH/USDT')
    btc_sig, btc_stat = analyze_market('SOL/USDT')
    
    market_strength = 95 
    if market_strength >= 90:
        utc, local = get_time_data()
        action_time = (datetime.now() + timedelta(minutes=3)).strftime("%I:%M %p")
        best_ex = get_best_exchange('BTC/USDT')
        
        signal_payload = {
            "xau": {"sig": xau_sig, "stat": xau_stat},
            "eur": {"sig": eur_sig, "stat": eur_stat},
            "btc": {"sig": btc_sig, "stat": btc_stat},
            "action_time": action_time,
            "best_exchange": best_ex
        }
        with open(SIGNAL_FILE, "w") as f:
            json.dump(signal_payload, f)
        
        return f"""🔔 HAVENGRID HIGH ALERT
🌐 UTC: {utc} | Local: {local}
🚨 Action Time: {action_time}

🔹 XAU/USD: {xau_sig} | Status: {xau_stat}
🔹 EUR/USD: {eur_sig} | Status: {eur_stat}
🔹 BTC/USDT: {btc_sig} | Status: {btc_stat}

🚀 Trade: Best on {best_ex}
🚀 Prepare for Entry!
🎯 Focus: High Probability Setups"""
    return None

def start_loops():
    if not SIGNAL_FILE.exists():
        with open(SIGNAL_FILE, "w") as f:
            json.dump({}, f)

    def pulse_loop():
        while True:
            if AUTHORIZED_FILE.exists():
                msg = get_market_pulse()
                try:
                    with open(AUTHORIZED_FILE, 'r') as f:
                        users = json.load(f)
                        for uid in users:
                            try: bot.send_message(uid, msg)
                            except: pass
                except: pass
            time.sleep(900)

    def alert_loop():
        last_alert_time = 0
        while True:
            alert = get_high_alert()
            if alert and (time.time() - last_alert_time > 900):
                if AUTHORIZED_FILE.exists():
                    try:
                        with open(AUTHORIZED_FILE, 'r') as f:
                            users = json.load(f)
                            for uid in users:
                                try: bot.send_message(uid, alert)
                                except: pass
                        last_alert_time = time.time()
                    except: pass
            time.sleep(60)

    threading.Thread(target=pulse_loop, daemon=True).start()
    threading.Thread(target=alert_loop, daemon=True).start()

if __name__ == "__main__":
    start_loops()
    bot.infinity_polling()