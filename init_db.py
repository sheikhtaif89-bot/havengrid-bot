import sqlite3

def init_db():
    conn = sqlite3.connect("havengrid_server.db")
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
    print("Database tables initialized successfully!")

if __name__ == "__main__":
    init_db()