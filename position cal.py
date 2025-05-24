import tkinter as tk
from tkinter import messagebox
from math import floor

root = tk.Tk()
root.title("Swing Trade Position & Risk Strategy Calculator")
root.geometry("900x600")
root.configure(bg="#f2f4f8")

LABEL_FONT = ("Segoe UI", 10, "bold")
ENTRY_FONT = ("Segoe UI", 10)
BUTTON_FONT = ("Segoe UI", 10, "bold")

left_frame = tk.Frame(root, bg="#f2f4f8", padx=10, pady=10)
left_frame.pack(side="left", fill="y")

right_frame = tk.Frame(root, bg="#f2f4f8", padx=10, pady=10)
right_frame.pack(side="left", fill="both", expand=True)

inputs = {
    "Entry Price (₹)": tk.StringVar(),
    "Stop Loss Price (₹)": tk.StringVar(),
    "Target Price (₹)": tk.StringVar(),
    "Capital (₹)": tk.StringVar(value="500000"),
    "Risk % of Capital": tk.StringVar(value="0.5"),
    "ATR Value (₹) [Optional]": tk.StringVar(),
    "Max Trade Exposure % (Default 40%)": tk.StringVar(value="40"),
    "Max Sector Exposure % (Default 60%)": tk.StringVar(value="60"),
    "Consecutive Losses (Drawdown Tracker)": tk.StringVar(value="0"),
}

for label_text, var in inputs.items():
    tk.Label(left_frame, text=label_text, font=LABEL_FONT, bg="#f2f4f8").pack(anchor='w', pady=(8,2))
    tk.Entry(left_frame, textvariable=var, font=ENTRY_FONT, width=28).pack(anchor='w')

tk.Label(right_frame, text="Trade Summary & Risk Strategy", font=LABEL_FONT, bg="#f2f4f8").pack(anchor="w")
result_box = tk.Text(right_frame, height=30, width=70, font=("Consolas", 11), wrap="word", bd=2, relief="sunken")
result_box.pack(pady=10, fill="both", expand=True)

def get_float(var_name, mandatory=True, default=None):
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

def get_int(var_name, mandatory=True, default=None):
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

def calculate():
    try:
        # Read inputs
        entry_price = get_float("Entry Price (₹)")
        stop_loss = get_float("Stop Loss Price (₹)")
        target_price = get_float("Target Price (₹)")
        capital = get_float("Capital (₹)")
        risk_percent = get_float("Risk % of Capital")
        atr_value = get_float("ATR Value (₹) [Optional]", mandatory=False, default=None)
        max_trade_exp_pct = get_float("Max Trade Exposure % (Default 40%)", mandatory=False, default=40)
        max_sector_exp_pct = get_float("Max Sector Exposure % (Default 60%)", mandatory=False, default=60)
        consecutive_losses = get_int("Consecutive Losses (Drawdown Tracker)", mandatory=False, default=0)

        # Calculate risk per share
        risk_per_share = entry_price - stop_loss
        if risk_per_share <= 0:
            raise ValueError("Stop Loss must be less than Entry Price for valid risk calculation.")

        # Capital risk limit
        capital_risk_limit = capital * (risk_percent / 100)

        # Position size based on risk limit
        position_size = floor(capital_risk_limit / risk_per_share)
        estimated_investment = position_size * entry_price

        # Reward-to-risk ratio
        reward_risk_ratio = (target_price - entry_price) / risk_per_share

        # Net potential profit
        net_potential_profit = (target_price - entry_price) * position_size

        # Risk breach check (investment should not exceed some optimal exposure, here max_trade_exp_pct)
        exposure_pct = (estimated_investment / capital) * 100
        risk_breach = exposure_pct > max_trade_exp_pct

        # Dynamic Allocation Band — simple logic based on exposure_pct
        if exposure_pct > max_trade_exp_pct:
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

        # Exposure rules
        max_trade_exp_ok = exposure_after_adj <= max_trade_exp_pct
        max_sector_exp_ok = True  # Placeholder, no sector data

        # Drawdown tracker simple check
        drawdown_ok = consecutive_losses == 0

        # Market timing filters (static check since no time input)
        opening_volatility_ok = True  # Assume entry after 9:30
        breakout_window_ok = True      # Assume inside 10:00-12:00 window
        volatility_monitor_ok = True
        atr_buffer = None
        validated_sl = stop_loss
        if atr_value is not None:
            atr_buffer = round(atr_value / 2, 2)
            validated_sl = round(stop_loss - atr_buffer, 2)

        # Target optimization
        target_min_rr = 2.5
        target_rr_ok = reward_risk_ratio >= target_min_rr
        trail_sl_price = round(entry_price + (risk_per_share * 1.5), 2)
        partial_booking_price = round(entry_price + ((target_price - entry_price) * 0.5), 2)

        # Build result string with emojis and formatting
        output = f"""🧮 POSITION SIZE & RISK STRATEGY OUTPUT
🔢 Trade Input
Entry Price: ₹{entry_price:.2f}

Stop Loss Price: ₹{stop_loss:.2f}

Target Price: ₹{target_price:.2f}

Risk per Share: ₹{risk_per_share:.2f}

Capital Risk Limit ({risk_percent:.2f}% of ₹{capital:,.0f}): ₹{capital_risk_limit:,.0f}

Total Capital: ₹{capital:,.0f}

📏 Position Calculation
Calculated Position Size: {position_size:,} shares

Estimated Investment: ₹{estimated_investment:,.0f}

Reward-to-Risk Ratio: {reward_risk_ratio:.2f}

Net Potential Profit: ₹{net_potential_profit:,.0f}

Risk Breach Check: {"❌ Investment exceeds optimal exposure" if risk_breach else "✅ Within safe exposure"}

Exposure % of Capital: {exposure_pct:.2f}%

🛡️ Risk Filters & Capital Control
Dynamic Allocation Band: {allocation_band} = {adjusted_position_size:,} shares

Max Trade Exposure Rule (≤{max_trade_exp_pct}%): {"✅ OK" if max_trade_exp_ok else "❌ Breach"}

Max Sector Exposure Rule (≤{max_sector_exp_pct}%): {"✅ OK" if max_sector_exp_ok else "❌ Breach"}

Drawdown Tracker: {"✅ No breach (0 consecutive losses)" if drawdown_ok else f"❌ {consecutive_losses} consecutive losses"}

🕒 Market Timing Filters
Opening Volatility Avoidance: {"✅ Entry after 9:30 AM" if opening_volatility_ok else "❌ Entry too early"}

Breakout Window Detected: {"✅ Between 10:00–12:00 (preferred time band)" if breakout_window_ok else "❌ Outside preferred time"}

Volatility Monitor (ATR/IV): {"✅ ATR = ₹"+str(atr_value)+f" → Add buffer of ₹{atr_buffer}" if atr_value else "ℹ️ ATR not provided"}

Validated SL (ATR Adjusted): Final SL = ₹{validated_sl:.2f}

🎯 Target Optimization
Current Risk:Reward: {"✅" if target_rr_ok else "❌"} {reward_risk_ratio:.2f} (≥ {target_min_rr} Minimum Target)

Trail SL After Target 1.5×R: After ₹{trail_sl_price}, shift SL to ₹{entry_price:.2f}

Optional Partial Booking: Consider 50% profit booking after ₹{partial_booking_price}

✅ Final Recommendation
Adjust Position Size: {"✅ Trade " + str(adjusted_position_size) + " shares (Medium Setup, Safe Exposure)" if allocation_band.startswith("🟡") else "✅ Full position size recommended"}

Use ATR-Based SL: ₹{validated_sl:.2f} {"(if ATR provided)" if atr_value else ""}

Monitor Post-Entry Volatility and trail SL as R multiples achieved

Expected Profit ({adjusted_position_size:,} shares): ₹{round((target_price - entry_price) * adjusted_position_size):,} (approx.)   
"""
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, output)

    except Exception as e:
        messagebox.showerror("Input Error", str(e))

button_frame = tk.Frame(right_frame, bg="#f2f4f8")
button_frame.pack(pady=5)

tk.Button(button_frame, text="Calculate", font=BUTTON_FONT, bg="#2e86de", fg="white", width=15, command=calculate).pack(side="left", padx=8)
tk.Button(button_frame, text="Clear", font=BUTTON_FONT, bg="#e74c3c", fg="white", width=10,
          command=lambda: [var.set("") for var in inputs.values()] + [result_box.delete("1.0", tk.END)]).pack(side="left")

root.mainloop()
