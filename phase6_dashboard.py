
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
