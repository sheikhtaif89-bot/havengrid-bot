import sqlite3

def check_db():
    try:
        conn = sqlite3.connect("havengrid_server.db")
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM aggregated_ohlcv")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM aggregated_ohlcv ORDER BY ts DESC LIMIT 5")
        rows = cursor.fetchall()
        print(f"Total records: {count}")
        for row in rows:
            print(row)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()