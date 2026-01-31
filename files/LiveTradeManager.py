import tkinter as tk
from tkinter import ttk

class LiveTradeManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Swing Trade Manager")
        self.root.geometry("500x400")

        self.entry_var = tk.DoubleVar()
        self.sl_var = tk.DoubleVar()
        self.qty_var = tk.IntVar()
        self.price_var = tk.DoubleVar()

        self.initial_risk = 0
        self.current_trail_sl = 0

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Entry Price").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.entry_var).grid(row=0, column=1)

        ttk.Label(frame, text="Stop Loss").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.sl_var).grid(row=1, column=1)

        ttk.Label(frame, text="Position Size (shares)").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.qty_var).grid(row=2, column=1)

        ttk.Label(frame, text="Current Price").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.price_var).grid(row=3, column=1)

        ttk.Button(frame, text="Start Trade", command=self.start_trade)\
            .grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(frame, text="Update Price", command=self.update_trade)\
            .grid(row=5, column=0, columnspan=2, pady=5)

        self.output = tk.Text(frame, height=12, width=55)
        self.output.grid(row=6, column=0, columnspan=2, pady=10)

    def log(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def start_trade(self):
        entry = self.entry_var.get()
        sl = self.sl_var.get()

        self.initial_risk = entry - sl
        self.current_trail_sl = sl

        self.output.delete("1.0", tk.END)
        self.log("Trade started")
        self.log(f"Initial Risk per share: {self.initial_risk:.2f}")
        self.log(f"Initial Stop Loss: {sl:.2f}")

    def update_trade(self):
        entry = self.entry_var.get()
        qty = self.qty_var.get()
        price = self.price_var.get()

        r_move = price - entry
        r_multiple = r_move / self.initial_risk if self.initial_risk > 0 else 0
        pnl = r_move * qty

        # trailing SL logic
        new_trail = price - self.initial_risk
        if new_trail > self.current_trail_sl:
            self.current_trail_sl = new_trail

        self.log(f"\nCurrent Price: {price:.2f}")
        self.log(f"P&L: {pnl:.2f}")
        self.log(f"R Multiple: {r_multiple:.2f}R")
        self.log(f"Trailing SL: {self.current_trail_sl:.2f}")

        # action suggestions
        if r_multiple >= 2:
            self.log("👉 Action: Book partial profits")
        elif r_multiple >= 1.5:
            self.log("👉 Action: Trail SL aggressively")
        elif r_multiple >= 1:
            self.log("👉 Action: Move SL to Entry (risk-free)")
        elif price <= self.current_trail_sl:
            self.log("❌ Stop hit. Exit trade.")
        else:
            self.log("⏳ Hold position")

if __name__ == "__main__":
    root = tk.Tk()
    app = LiveTradeManager(root)
    root.mainloop()
