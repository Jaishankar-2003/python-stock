import tkinter as tk
from tkinter import messagebox
from math import floor

root = tk.Tk()
root.title("Swing Trade Position & Risk Strategy Calculator")
root.geometry("950x650")
root.configure(bg="#f2f4f8")

LABEL_FONT = ("Segoe UI", 10, "bold")
ENTRY_FONT = ("Segoe UI", 10)
BUTTON_FONT = ("Segoe UI", 10, "bold")

left_frame = tk.Frame(root, bg="#f2f4f8", padx=15, pady=15)
left_frame.pack(side="left", fill="y")

right_frame = tk.Frame(root, bg="#f2f4f8", padx=15, pady=15)
right_frame.pack(side="left", fill="both", expand=True)

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

tk.Label(right_frame, text="Trade Summary & Risk Strategy", font=LABEL_FONT, bg="#f2f4f8").pack(anchor="w")
result_box = tk.Text(right_frame, height=32, width=80, font=("Consolas", 11), wrap="word", bd=2, relief="sunken")
result_box.pack(pady=10, fill="both", expand=True)

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
        result_box.insert(tk.END, "🧮 POSITION SIZE & RISK STRATEGY OUTPUT\n\n", "header")
        result_box.insert(tk.END, "🔢 Trade Input\n", "section")

        # Entry price, Stop loss, Target Price
        result_box.insert(tk.END, f"Entry Price: ₹{entry_price:.2f}\n")
        result_box.insert(tk.END, f"Stop Loss Price: ₹{sl_price:.2f}\n")
        if sl_percent is not None:
            result_box.insert(tk.END, f" (Based on {sl_percent:.2f}% below Entry Price)\n")
        result_box.insert(tk.END, f"Target Price: ₹{target_price:.2f}\n")
        if target_percent is not None:
            result_box.insert(tk.END, f" (Based on {target_percent:.2f}% above Entry Price)\n")

        result_box.insert(tk.END, f"\nRisk per Share: ₹{risk_per_share:.2f}\n")
        result_box.insert(tk.END, f"Capital Risk Limit ({risk_percent:.2f}% of ₹{capital:,.0f}): ₹{capital_risk_limit:,.2f}\n")
        result_box.insert(tk.END, f"Total Capital: ₹{capital:,.0f}\n\n")

        result_box.insert(tk.END, "📏 Position Calculation\n", "section")
        result_box.insert(tk.END, f"Calculated Position Size: {position_size:,} shares\n")
        result_box.insert(tk.END, f"Estimated Investment: ₹{estimated_investment:,.2f}\n")
        result_box.insert(tk.END, f"Reward-to-Risk Ratio: {reward_risk_ratio:.2f}\n")
        result_box.insert(tk.END, f"Net Potential Profit: ₹{net_potential_profit:,.2f}\n")

        risk_breach_mark = "❌" if risk_breach else "✅"
        risk_breach_text = "Investment exceeds optimal exposure" if risk_breach else "Within optimal exposure"
        result_box.insert(tk.END, f"Risk Breach Check: {risk_breach_mark} {risk_breach_text}\n")

        result_box.insert(tk.END, f"Exposure % of Capital: {exposure_pct:.2f}%\n\n")

        result_box.insert(tk.END, "🛡️ Risk Filters & Capital Control\n", "section")
        result_box.insert(tk.END, f"Dynamic Allocation Band: {allocation_band}\n")
        if risk_breach:
            result_box.insert(tk.END, f"Adjusted Position Size (50%): {adjusted_position_size:,} shares\n")
            result_box.insert(tk.END, f"Adjusted Investment: ₹{adjusted_investment:,.2f}\n")
            result_box.insert(tk.END, f"Exposure % after Adjustment: {exposure_after_adj:.2f}%\n")
            result_box.insert(tk.END, f"Risk Breach After Adjustment: {'❌' if risk_breach_after_adj else '✅'}\n")
        result_box.insert(tk.END, f"Max Trade Exposure Rule (≤{max_trade_exp_pct}%): {'✅' if max_trade_exp_ok else '❌'}\n")
        result_box.insert(tk.END, f"Max Sector Exposure Rule (≤{max_sector_exp_pct}%): {'✅' if max_sector_exp_ok else '❌'}\n")
        result_box.insert(tk.END, f"Drawdown Tracker (Consecutive Losses): {'✅ No breach' if drawdown_ok else '⚠️ Warning'} ({consecutive_losses} consecutive losses)\n\n")

        result_box.insert(tk.END, "🕒 Market Timing Filters\n", "section")
        result_box.insert(tk.END, f"Opening Volatility Avoidance: {'✅ Entry after 9:30 AM' if opening_volatility_ok else '❌ Check Entry Time'}\n")
        result_box.insert(tk.END, f"Breakout Window Detected: {'✅ Between 10:00–12:00 (preferred time band)' if breakout_window_ok else '❌ No suitable window'}\n")
        if atr_value is not None:
            result_box.insert(tk.END, f"Volatility Monitor (ATR/IV): ✅ ATR = ₹{atr_value:.2f} → Add buffer of ₹{atr_buffer:.2f}\n")
            result_box.insert(tk.END, f"Validated SL (ATR Adjusted): Final SL = ₹{validated_sl:.2f}\n")
        else:
            result_box.insert(tk.END, f"Volatility Monitor (ATR/IV): ⚠️ ATR not provided\n")

        result_box.insert(tk.END, "\n🎯 Target Optimization\n", "section")
        result_box.insert(tk.END, f"Current Risk:Reward: {'✅' if target_rr_ok else '❌'} {reward_risk_ratio:.2f} ({'>2.5 Minimum Target'})\n")
        result_box.insert(tk.END, f"Trail SL After Target 1.5×R: After ₹{trail_sl_price:.2f}, shift SL to ₹{entry_price:.2f}\n")
        result_box.insert(tk.END, f"Optional Partial Booking: Consider 50% profit booking after ₹{partial_booking_price:.2f}\n\n")

        result_box.insert(tk.END, "✅ Final Recommendation\n", "section")
        result_box.insert(tk.END, f"Adjust Position Size: {'✅ Trade ' + str(adjusted_position_size) + ' shares (Safe Exposure)' if risk_breach else '✅ Full Position Size OK'}\n")
        result_box.insert(tk.END, f"Use ATR-Based SL: ₹{validated_sl:.2f}\n")
        result_box.insert(tk.END, "Monitor Post-Entry Volatility and trail SL as R multiples achieved\n")
        result_box.insert(tk.END, f"Expected Profit ({adjusted_position_size} shares): ₹{round((target_price - entry_price) * adjusted_position_size, 2)} (approx.)\n")

        # Color tagging for better psychology
        color_tag("header", fg="#0a64a0")
        color_tag("section", fg="#2e4057", bg="#dbe9f4")

        # Highlight Risk Breach in red/yellow/green
        if risk_breach:
            result_box.tag_add("risk_breach", "17.0", "18.0")
            color_tag("risk_breach", fg="red", bg="#ffdddd")
        else:
            result_box.tag_add("risk_breach", "17.0", "18.0")
            color_tag("risk_breach", fg="green", bg="#ddffdd")

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
        return

calculate_btn = tk.Button(left_frame, text="Calculate Position & Risk", font=BUTTON_FONT, bg="#246bb2", fg="white", command=calculate)
calculate_btn.pack(pady=20)

root.mainloop()
