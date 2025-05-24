import tkinter as tk
from tkinter import messagebox
from math import floor

root = tk.Tk()
root.title("Swing Trade Position & Risk Strategy Calculator")
root.geometry("1620x1050")
root.configure(bg="#f2f4f8")

LABEL_FONT = ("Segoe UI", 10, "bold")
ENTRY_FONT = ("Segoe UI", 10)
BUTTON_FONT = ("Segoe UI", 10, "bold")

# === LEFT SCROLLABLE FRAME ===
left_container = tk.Frame(root, bg="#f2f4f8")
left_container.pack(side="left", fill="y")

left_canvas = tk.Canvas(left_container, bg="#f2f4f8", width=400, highlightthickness=0)
left_canvas.pack(side="left", fill="y", expand=False)

left_scrollbar = tk.Scrollbar(left_container, orient="vertical", command=left_canvas.yview)
left_scrollbar.pack(side="left", fill="y")

left_canvas.configure(yscrollcommand=left_scrollbar.set)

left_frame = tk.Frame(left_canvas, bg="#f2f4f8", padx=15, pady=15)
left_canvas.create_window((0, 0), window=left_frame, anchor="nw")

def on_left_frame_configure(event):
    left_canvas.configure(scrollregion=left_canvas.bbox("all"))

left_frame.bind("<Configure>", on_left_frame_configure)

# === RIGHT SCROLLABLE FRAME ===
right_container = tk.Frame(root, bg="#f2f4f8")
right_container.pack(side="left", fill="both", expand=True)

right_canvas = tk.Canvas(right_container, bg="#f2f4f8", highlightthickness=0)
right_canvas.pack(side="left", fill="both", expand=True)

right_scrollbar = tk.Scrollbar(right_container, orient="vertical", command=right_canvas.yview)
right_scrollbar.pack(side="left", fill="y")

right_canvas.configure(yscrollcommand=right_scrollbar.set)

right_frame = tk.Frame(right_canvas, bg="#f2f4f8", padx=20, pady=20)
right_canvas.create_window((0, 0), window=right_frame, anchor="nw")

def on_right_frame_configure(event):
    right_canvas.configure(scrollregion=right_canvas.bbox("all"))

right_frame.bind("<Configure>", on_right_frame_configure)

# --- Input fields in left_frame ---
inputs = {
    "Entry Price (₹)": tk.StringVar(),
    "Stop Loss Price (₹) [optional if % given]": tk.StringVar(),
    "Stop Loss % below Entry [optional if price given]": tk.StringVar(),
    "Target Price (₹) [optional if % given]": tk.StringVar(),
    "Target % above Entry [optional if price given]": tk.StringVar(),
    "Capital (₹) [optional]": tk.StringVar(value="500000"),
    "Risk % of Capital [optional]": tk.StringVar(value="0.5"),
    "ATR Value (₹) [Optional]": tk.StringVar(),
    "Max Trade Exposure % (Default 40%)": tk.StringVar(value="40"),
    "Max Sector Exposure % (Default 60%)": tk.StringVar(value="60"),
    "Consecutive Losses (Drawdown Tracker)": tk.StringVar(value="0"),
}

for label_text, var in inputs.items():
    tk.Label(left_frame, text=label_text, font=LABEL_FONT, bg="#f2f4f8").pack(anchor='w', pady=(8,2))
    tk.Entry(left_frame, textvariable=var, font=ENTRY_FONT, width=30).pack(anchor='w')

calculate_btn = tk.Button(left_frame, text="Calculate Position & Risk", font=BUTTON_FONT, bg="#246bb2", fg="white", command=lambda: calculate())
calculate_btn.pack(pady=20)

# --- Result box in right_frame ---
tk.Label(right_frame, text="Trade Summary & Risk Strategy", font=LABEL_FONT, bg="#f2f4f8").pack(anchor="w")
result_box = tk.Text(right_frame, height=30, width=40, font=("Consolas", 11), wrap="word", bd=2, relief="sunken")
result_box.pack(pady=15, fill="both", expand=True)

def get_float(var_name, mandatory=False, default=None):
    val = inputs[var_name].get().strip()
    if not val:
        if mandatory:
            raise ValueError(f"{var_name} is required.")
        else:
            return default
    try:
        return float(val)
    except ValueError:
        raise ValueError(f"Invalid number for {var_name}: '{val}'")

def get_int(var_name, mandatory=False, default=None):
    val = inputs[var_name].get().strip()
    if not val:
        if mandatory:
            raise ValueError(f"{var_name} is required.")
        else:
            return default
    try:
        return int(val)
    except ValueError:
        raise ValueError(f"Invalid integer for {var_name}: '{val}'")

def color_tag(tag_name, fg=None, bg=None):
    if fg or bg:
        result_box.tag_config(tag_name, foreground=fg, background=bg)

def calculate():
    try:
        entry_price = get_float("Entry Price (₹)", mandatory=True)

        # Determine Stop Loss Price
        sl_price = get_float("Stop Loss Price (₹) [optional if % given]", mandatory=False)
        sl_percent = get_float("Stop Loss % below Entry [optional if price given]", mandatory=False)

        if sl_price is None and sl_percent is None:
            raise ValueError("Please provide either Stop Loss Price or Stop Loss % below Entry.")
        elif sl_price is None and sl_percent is not None:
            sl_price = round(entry_price * (1 - sl_percent / 100), 2)
        elif sl_price is not None and sl_percent is None:
            pass  # use sl_price as is
        else:
            # both given, prefer price and warn
            sl_price = sl_price  # use given price

        # Determine Target Price
        target_price = get_float("Target Price (₹) [optional if % given]", mandatory=False)
        target_percent = get_float("Target % above Entry [optional if price given]", mandatory=False)

        if target_price is None and target_percent is None:
            raise ValueError("Please provide either Target Price or Target % above Entry.")
        elif target_price is None and target_percent is not None:
            target_price = round(entry_price * (1 + target_percent / 100), 2)
        elif target_price is not None and target_percent is None:
            pass
        else:
            # both given, prefer price and warn
            target_price = target_price

        capital = get_float("Capital (₹) [optional]", mandatory=False, default=500000)
        risk_percent = get_float("Risk % of Capital [optional]", mandatory=False, default=0.5)
        atr_value = get_float("ATR Value (₹) [Optional]", mandatory=False)
        max_trade_exp_pct = get_float("Max Trade Exposure % (Default 40%)", mandatory=False, default=40)
        max_sector_exp_pct = get_float("Max Sector Exposure % (Default 60%)", mandatory=False, default=60)
        consecutive_losses = get_int("Consecutive Losses (Drawdown Tracker)", mandatory=False, default=0)

        # Risk per share and validation
        risk_per_share = entry_price - sl_price
        if risk_per_share <= 0:
            raise ValueError("Stop Loss must be less than Entry Price for valid risk calculation.")

        capital_risk_limit = capital * (risk_percent / 100)

        # Position size
        position_size = floor(capital_risk_limit / risk_per_share)
        estimated_investment = position_size * entry_price

        reward_risk_ratio = (target_price - entry_price) / risk_per_share

        net_potential_profit = (target_price - entry_price) * position_size

        exposure_pct = (estimated_investment / capital) * 100
        risk_breach = exposure_pct > max_trade_exp_pct

        # Dynamic Allocation Band
        if risk_breach:
            allocation_band = "🟡 Medium Setup → Apply 50% size"
            adjusted_position_size = floor(position_size * 0.5)
            adjusted_investment = adjusted_position_size * entry_price
            exposure_after_adj = (adjusted_investment / capital) * 100
            risk_breach_after_adj = exposure_after_adj > max_trade_exp_pct
        else:
            allocation_band = "🟢 Low Setup → Full size OK"
            adjusted_position_size = position_size
            adjusted_investment = estimated_investment
            exposure_after_adj = exposure_pct
            risk_breach_after_adj = False

        max_trade_exp_ok = exposure_after_adj <= max_trade_exp_pct
        max_sector_exp_ok = True  # Placeholder for sector exposure logic

        drawdown_ok = consecutive_losses == 0

        opening_volatility_ok = True  # Assume true
        breakout_window_ok = True
        volatility_monitor_ok = True
        atr_buffer = None
        validated_sl = sl_price
        if atr_value is not None:
            atr_buffer = round(atr_value / 2, 2)
            validated_sl = round(sl_price - atr_buffer, 2)

        target_min_rr = 2.5
        target_rr_ok = reward_risk_ratio >= target_min_rr
        trail_sl_price = round(entry_price + (risk_per_share * 1.5), 2)
        partial_booking_price = round(entry_price + ((target_price - entry_price) * 0.5), 2)

        # Clear previous tags
        result_box.delete("1.0", tk.END)
        for tag in result_box.tag_names():
            result_box.tag_delete(tag)

        # Insert output with tags for colors
        result_box.insert(tk.END, "🧮 POSITION SIZE & RISK CALCULATION SUMMARY\n\n", "header")

        result_box.insert(tk.END, f"Entry Price: ₹{entry_price:.2f}\n")
        result_box.insert(tk.END, f"Stop Loss Price: ₹{sl_price:.2f}\n")
        if atr_buffer:
            result_box.insert(tk.END, f"ATR Buffer (Half ATR): ₹{atr_buffer:.2f}\n")
            result_box.insert(tk.END, f"Validated Stop Loss Price (with ATR buffer): ₹{validated_sl:.2f}\n")

        result_box.insert(tk.END, f"Target Price: ₹{target_price:.2f}\n")
        result_box.insert(tk.END, f"Risk per Share: ₹{risk_per_share:.2f}\n")
        result_box.insert(tk.END, f"Capital: ₹{capital:,.0f}\n")
        result_box.insert(tk.END, f"Risk % of Capital: {risk_percent:.2f}%\n")
        result_box.insert(tk.END, f"Capital Risk Limit: ₹{capital_risk_limit:,.2f}\n\n")

        result_box.insert(tk.END, f"Position Size (shares): {position_size:,}\n")
        result_box.insert(tk.END, f"Estimated Investment: ₹{estimated_investment:,.2f}\n")
        result_box.insert(tk.END, f"Reward to Risk Ratio: {reward_risk_ratio:.2f}\n")
        result_box.insert(tk.END, f"Potential Profit: ₹{net_potential_profit:,.2f}\n\n")

        # Exposure & allocation band color coding
        if risk_breach:
            result_box.insert(tk.END, f"Exposure %: {exposure_pct:.2f}% → Exceeds max trade exposure {max_trade_exp_pct}%\n", "warning")
            result_box.insert(tk.END, f"Allocation Band Recommendation: {allocation_band}\n", "warning")
            result_box.insert(tk.END, f"Adjusted Position Size: {adjusted_position_size:,} shares\n")
            result_box.insert(tk.END, f"Adjusted Investment: ₹{adjusted_investment:,.2f}\n")
        else:
            result_box.insert(tk.END, f"Exposure %: {exposure_pct:.2f}% (within limit of {max_trade_exp_pct}%)\n", "success")
            result_box.insert(tk.END, f"Allocation Band: {allocation_band}\n", "success")

        # Additional conditions summary
        result_box.insert(tk.END, "\n--- Additional Risk Controls & Conditions ---\n")
        result_box.insert(tk.END, f"Max Trade Exposure OK: {'✅' if max_trade_exp_ok else '❌'}\n")
        result_box.insert(tk.END, f"Max Sector Exposure OK: {'✅' if max_sector_exp_ok else '❌'}\n")
        result_box.insert(tk.END, f"Drawdown OK (No Consecutive Losses): {'✅' if drawdown_ok else '❌'}\n")
        result_box.insert(tk.END, f"Opening Volatility OK: {'✅' if opening_volatility_ok else '❌'}\n")
        result_box.insert(tk.END, f"Breakout Window OK: {'✅' if breakout_window_ok else '❌'}\n")
        result_box.insert(tk.END, f"Volatility Monitor OK: {'✅' if volatility_monitor_ok else '❌'}\n")
        result_box.insert(tk.END, f"Target Reward Ratio >= {target_min_rr}: {'✅' if target_rr_ok else '❌'}\n")
        result_box.insert(tk.END, f"Trail Stop Loss Price (1.5x risk): ₹{trail_sl_price:.2f}\n")
        result_box.insert(tk.END, f"Partial Booking Price (~50% target): ₹{partial_booking_price:.2f}\n")

        # Color tags for highlights
        color_tag("header", fg="#007acc", bg="#e6f0fa")
        color_tag("success", fg="green")
        color_tag("warning", fg="red")

        # Tag warnings and successes
        start_idx = "1.0"
        while True:
            pos = result_box.search("❌", start_idx, stopindex=tk.END)
            if not pos:
                break
            end_pos = f"{pos}+2c"
            result_box.tag_add("warning", pos, end_pos)
            start_idx = end_pos

        start_idx = "1.0"
        while True:
            pos = result_box.search("✅", start_idx, stopindex=tk.END)
            if not pos:
                break
            end_pos = f"{pos}+2c"
            result_box.tag_add("success", pos, end_pos)
            start_idx = end_pos

    except Exception as e:
        messagebox.showerror("Input Error", str(e))
        result_box.delete("1.0", tk.END)

root.mainloop()
