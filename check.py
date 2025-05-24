import tkinter as tk
from tkinter import messagebox
from math import floor

def calculate():
    try:
        entry_price = float(entry_price_entry.get())
        capital_input = capital_entry.get()
        capital = float(capital_input) if capital_input else 0

        risk_percent_input = risk_percent_entry.get()
        risk_percent = float(risk_percent_input) if risk_percent_input else None

        atr = float(atr_entry.get()) if atr_entry.get() else 0
        manual_position = manual_position_entry.get()
        reward_ratio = float(reward_ratio_entry.get()) if reward_ratio_entry.get() else None
        reward_percent = float(reward_percent_entry.get()) if reward_percent_entry.get() else None

        # Determine Target Price
        target_price_input = target_price_entry.get()
        if reward_percent is not None:
            target_price = round(entry_price * (1 + reward_percent / 100), 2)
        elif target_price_input:
            target_price = float(target_price_input)
        else:
            messagebox.showerror("Missing Data", "Enter either Reward % or Target Price.")
            return

        # Determine Stop Loss
        stop_loss_input = stop_loss_entry.get()
        stop_loss = float(stop_loss_input) if stop_loss_input else None
        if stop_loss is None:
            if reward_ratio is None:
                messagebox.showerror("Missing Data", "Enter Stop Loss or Target Reward Ratio.")
                return
            risk_per_share = (target_price - entry_price) / reward_ratio
            stop_loss = round(entry_price - risk_per_share, 2)
        else:
            risk_per_share = round(entry_price - stop_loss, 2)

        if risk_per_share <= 0:
            messagebox.showerror("Invalid Inputs", "Stop Loss must be less than Entry Price.")
            return

        # Capital Risk Calculations (optional)
        if risk_percent is not None and capital > 0:
            capital_risk = round(capital * (risk_percent / 100), 2)
            position_size = floor(capital_risk / risk_per_share)
        elif manual_position:
            position_size = int(manual_position)
            capital_risk = round(position_size * risk_per_share, 2)
        else:
            messagebox.showerror("Missing Data", "Enter either Capital & Risk % or Manual Position Size.")
            return

        investment = round(position_size * entry_price, 2)
        net_profit = round(position_size * (target_price - entry_price), 2)
        reward_risk_ratio = round((target_price - entry_price) / risk_per_share, 2)
        adjusted_sl = round(stop_loss - (atr * 0.5), 2) if atr else "N/A"

        recommended_size = floor(position_size * 0.5)
        recommended_investment = round(recommended_size * entry_price, 2)
        trail_sl_price = round(entry_price + 1.5 * risk_per_share, 2)
        partial_booking_price = round(entry_price + 2.5 * risk_per_share, 2)

        result = f"""
==================== TRADE SUMMARY ====================
Entry Price: ₹{entry_price}
Target Price: ₹{target_price} {'(Auto)' if reward_percent is not None else ''}
Stop Loss: ₹{stop_loss} {'(Auto)' if stop_loss_input == '' else ''}
Reward/Share: ₹{round(target_price - entry_price, 2)}
Risk/Share: ₹{round(risk_per_share, 2)}
Reward-to-Risk Ratio: {reward_risk_ratio}

Position Size: {position_size} shares
Investment: ₹{investment}
Potential Net Profit: ₹{net_profit}
Capital Risk: ₹{capital_risk if capital_risk else 'Manual'}

==================== RISK STRATEGY ====================
Recommended Size (50%): {recommended_size} shares
Recommended Investment: ₹{recommended_investment}
ATR-based Adjusted SL: ₹{adjusted_sl}
Trail SL After Price: ₹{trail_sl_price}
Partial Booking After Price: ₹{partial_booking_price}
=======================================================
"""
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, result)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric inputs.")

# ============ GUI Setup ============ #
root = tk.Tk()
root.title("Swing Trade Position & Risk Calculator")
root.geometry("850x800")
root.configure(bg="#ecf2f9")

label_opts = {'padx': 10, 'pady': 8, 'sticky': 'w'}
entry_opts = {'padx': 10, 'pady': 5, 'width': 25}

# --- INPUT FIELDS --- #
tk.Label(root, text="Entry Price (₹):", bg="#ecf2f9").grid(row=0, column=0, **label_opts)
entry_price_entry = tk.Entry(root)
entry_price_entry.grid(row=0, column=1, **entry_opts)

tk.Label(root, text="Reward % (Optional):", bg="#ecf2f9").grid(row=1, column=0, **label_opts)
reward_percent_entry = tk.Entry(root)
reward_percent_entry.grid(row=1, column=1, **entry_opts)

tk.Label(root, text="Target Price (₹) [if no Reward %]:", bg="#ecf2f9").grid(row=2, column=0, **label_opts)
target_price_entry = tk.Entry(root)
target_price_entry.grid(row=2, column=1, **entry_opts)

tk.Label(root, text="Stop Loss (₹) [Optional]:", bg="#ecf2f9").grid(row=3, column=0, **label_opts)
stop_loss_entry = tk.Entry(root)
stop_loss_entry.grid(row=3, column=1, **entry_opts)

tk.Label(root, text="Target Reward Ratio (R:R):", bg="#ecf2f9").grid(row=4, column=0, **label_opts)
reward_ratio_entry = tk.Entry(root)
reward_ratio_entry.grid(row=4, column=1, **entry_opts)

tk.Label(root, text="Capital (₹):", bg="#ecf2f9").grid(row=5, column=0, **label_opts)
capital_entry = tk.Entry(root)
capital_entry.insert(0, "500000")
capital_entry.grid(row=5, column=1, **entry_opts)

tk.Label(root, text="Risk % of Capital [Optional]:", bg="#ecf2f9").grid(row=6, column=0, **label_opts)
risk_percent_entry = tk.Entry(root)
risk_percent_entry.insert(0, "")
risk_percent_entry.grid(row=6, column=1, **entry_opts)

tk.Label(root, text="ATR Value [Optional]:", bg="#ecf2f9").grid(row=7, column=0, **label_opts)
atr_entry = tk.Entry(root)
atr_entry.grid(row=7, column=1, **entry_opts)

tk.Label(root, text="Manual Position Size [Optional]:", bg="#ecf2f9").grid(row=8, column=0, **label_opts)
manual_position_entry = tk.Entry(root)
manual_position_entry.grid(row=8, column=1, **entry_opts)

# --- Calculate Button --- #
tk.Button(root, text="Calculate",
          command=calculate,
          bg="#28a745", fg="white", font=("Arial", 12, "bold"),
          width=20).grid(row=9, column=1, pady=20)

# --- Output Box --- #
output_text = tk.Text(root, height=25, width=100, wrap=tk.WORD, font=("Courier New", 10))
output_text.grid(row=10, column=0, columnspan=3, padx=15, pady=10)

root.mainloop()
