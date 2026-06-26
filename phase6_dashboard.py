import customtkinter as ctk
import json
import threading
import time
from pathlib import Path

# Configuration
SIGNALS_FILE = Path(__file__).parent / "signals.json"

class HavengridDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Havengrid Pro Dashboard - Phase 6")
        self.geometry("600x450")
        ctk.set_appearance_mode("dark")
        
        # Tabview for sections
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add("Live Signals")
        self.tabview.add("24h Analysis")
        self.tabview.add("30d Performance")
        
        # Live Signals UI
        self.live_label = ctk.CTkLabel(self.tabview.tab("Live Signals"), text="Waiting for signals...", font=("Arial", 16))
        self.live_label.pack(pady=40)
        
        # 24h & 30d Labels
        self.day_label = ctk.CTkLabel(self.tabview.tab("24h Analysis"), text="Processing 24h data...")
        self.day_label.pack(pady=20)
        
        self.month_label = ctk.CTkLabel(self.tabview.tab("30d Performance"), text="Processing 30d history...")
        self.month_label.pack(pady=20)
        
        # Start background polling
        self.run_polling()

    def run_polling(self):
        def poll():
            while True:
                if SIGNALS_FILE.exists():
                    try:
                        with open(SIGNALS_FILE, "r") as f:
                            data = json.load(f)
                            if data:
                                latest = data[-1]
                                # Using after() for thread-safe UI updates
                                self.after(0, lambda: self.update_dashboard(latest, data))
                    except: 
                        pass
                time.sleep(3)
        threading.Thread(target=poll, daemon=True).start()

    def update_dashboard(self, latest, data):
        self.live_label.configure(text=f"Asset: {latest['asset']}\nPrice: {latest['price']}\nSL: {latest['sl']} | TP: {latest['tp']}")
        self.day_label.configure(text=f"24h Signals Count: {len(data[-5:])}") 
        self.month_label.configure(text=f"Total Signals Recorded: {len(data)}")

def main():
    app = HavengridDashboard()
    app.mainloop()

if __name__ == "__main__":
    main()