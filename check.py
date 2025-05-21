import tkinter as tk
from tkinter import messagebox, scrolledtext
import tkinter.font as tkfont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# --- Trade calculation function ---
def general_trade_calculator(
    capital=None,
    entry_price=None,
    stop_loss_price=None,
    target_price=None,
    risk_perc=None,
    reward_ratio=None,
    manual_position_size=None
):
    if not capital or not entry_price:
        return "❌ Capital and Entry Price are required."

    if stop_loss_price:
        risk_per_share = entry_price - stop_loss_price
        if risk_per_share <= 0:
            return "❌ Stop-loss must be below entry price."
    elif risk_perc and capital:
        risk_amount = capital * (risk_perc / 100)
        risk_per_share = risk_amount / (capital / entry_price)
        stop_loss_price = entry_price - risk_per_share
    else:
        return "❌ Either Stop-Loss Price or Risk % is required."

    if manual_position_size:
        position_size = manual_position_size
        risk_amount = risk_per_share * position_size
    else:
        risk_amount = capital * (risk_perc / 100) if risk_perc else risk_per_share * (capital // entry_price)
        position_size = int(risk_amount // risk_per_share)

    invested_amount = position_size * entry_price

    if reward_ratio and not target_price:
        reward_per_share = risk_per_share * reward_ratio
        target_price = entry_price + reward_per_share
    elif target_price:
        reward_per_share = target_price - entry_price
        reward_ratio = reward_per_share / risk_per_share
    else:
        return "❌ Either Target Price or Reward Ratio is required."

    expected_profit = reward_per_share * position_size
    percent_gain = (expected_profit / capital) * 100

    return {
        "Entry Price": entry_price,
        "Stop-Loss Price": round(stop_loss_price, 2),
        "Target Price": round(target_price, 2),
        "Risk per Share": round(risk_per_share, 2),
        "Reward per Share": round(reward_per_share, 2),
        "Reward Ratio": round(reward_ratio, 2),
        "Risk Amount (₹)": round(risk_amount, 2),
        "Position Size": position_size,
        "Invested Amount (₹)": round(invested_amount, 2),
        "Expected Profit (₹)": round(expected_profit, 2),
        "Expected % Gain": round(percent_gain, 2),
    }

# --- Position Size Only Mini Calculator ---
def calculate_position_size():
    try:
        capital = float(entry_calc_capital.get())
        entry_price = float(entry_calc_entry.get())
        stop_loss = float(entry_calc_stop.get())
        risk_perc = float(entry_calc_risk.get())

        risk_per_share = entry_price - stop_loss
        risk_amount = capital * (risk_perc / 100)
        position_size = int(risk_amount // risk_per_share)

        result_position_calc.config(state='normal')
        result_position_calc.delete("1.0", tk.END)
        result_position_calc.insert(tk.END, f"Calculated Position Size: {position_size} shares\n")
        result_position_calc.insert(tk.END, f"Risk per Share: ₹{risk_per_share:.2f}\n")
        result_position_calc.insert(tk.END, f"Total Risk Amount: ₹{risk_amount:.2f}")
        result_position_calc.config(state='disabled')
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

# --- Full Calculation Button ---
def calculate():
    try:
        capital = float(entry_capital.get())
        entry = float(entry_entry.get())
        stop_loss = float(entry_stop_loss.get()) if entry_stop_loss.get() else None
        target = float(entry_target.get()) if entry_target.get() else None
        risk_perc = float(entry_risk_perc.get()) if entry_risk_perc.get() else None
        reward_ratio = float(entry_reward_ratio.get()) if entry_reward_ratio.get() else None
        manual_pos_size = int(entry_position_size.get()) if entry_position_size.get() else None

        result = general_trade_calculator(
            capital=capital,
            entry_price=entry,
            stop_loss_price=stop_loss,
            target_price=target,
            risk_perc=risk_perc,
            reward_ratio=reward_ratio,
            manual_position_size=manual_pos_size
        )

        output_text.config(state='normal')
        output_text.delete("1.0", tk.END)

        if isinstance(result, dict):
            output_text.insert(tk.END, "📊 Trade Plan Summary:\n\n", "bold")
            for key, value in result.items():
                tag = None
                if "Risk" in key:
                    tag = "risk"
                elif "Stop-Loss" in key:
                    tag = "stop"
                elif "Expected Profit" in key:
                    tag = "profit"
                elif "Expected % Gain" in key:
                    tag = "gain"
                if tag:
                    output_text.insert(tk.END, f"{key}: {value}\n", tag)
                else:
                    output_text.insert(tk.END, f"{key}: {value}\n")
            update_chart(result["Entry Price"], result["Stop-Loss Price"], result["Target Price"])
        else:
            output_text.insert(tk.END, result)
            clear_chart()

        output_text.config(state='disabled')
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

def update_chart(entry_price, stop_loss_price, target_price):
    ax.clear()
    ax.set_title("Trade Setup Chart", fontsize=16)
    ax.set_ylabel("Price (₹)", fontsize=14)
    ax.set_xticks([])
    prices = [stop_loss_price, entry_price, target_price]
    labels = ["Stop Loss", "Entry", "Target"]

    ax.plot([1, 2, 3], prices, marker='o', linestyle='-', color='black')
    for i, (x, y) in enumerate(zip([1, 2, 3], prices)):
        ax.text(x, y, f"{labels[i]}:\n₹{y}", ha='center', va='bottom', fontweight='bold', fontsize=13)
    canvas.draw()

def clear_chart():
    ax.clear()
    canvas.draw()

# --- GUI Setup ---
root = tk.Tk()
root.title("📈 Advanced Swing Trade Calculator")
root.state("zoomed")  # Fullscreen

# Fonts
font_label = tkfont.Font(family="Arial", size=14)
font_entry = tkfont.Font(family="Arial", size=14)
font_output = tkfont.Font(family="Consolas", size=14)
font_bold = tkfont.Font(family="Arial", size=15, weight="bold")

# --- Frames ---
frame_output = tk.Frame(root, padx=10, pady=10)
frame_input = tk.Frame(root, padx=10, pady=10)
frame_chart = tk.Frame(root, padx=10, pady=10)
frame_calc = tk.Frame(root, padx=10, pady=10, relief=tk.RIDGE, bd=2)

frame_output.grid(row=0, column=0, sticky="nsew")
frame_input.grid(row=0, column=1, sticky="nsew")
frame_chart.grid(row=0, column=2, sticky="nsew")
frame_calc.grid(row=0, column=3, sticky="nsew")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_rowconfigure(0, weight=1)

# --- Output Section ---
output_text = scrolledtext.ScrolledText(frame_output, font=font_output, width=40, height=30)
output_text.pack(expand=True, fill="both")

output_text.tag_configure("bold", font=font_bold)
output_text.tag_configure("risk", foreground="red", font=font_bold)
output_text.tag_configure("profit", foreground="green", font=font_bold)
output_text.tag_configure("gain", foreground="blue", font=font_bold)
output_text.tag_configure("stop", foreground="orange", font=font_bold)

# --- Input Field Generator ---
def add_input(parent, label):
    frame = tk.Frame(parent)
    frame.pack(fill="x", pady=6)
    tk.Label(frame, text=label, font=font_label).pack(anchor="w")
    entry = tk.Entry(frame, font=font_entry)
    entry.pack(fill="x")
    return entry

entry_capital = add_input(frame_input, "💰 Capital (₹):")
entry_entry = add_input(frame_input, "📌 Entry Price (₹):")
entry_stop_loss = add_input(frame_input, "🛑 Stop-Loss Price (₹):")
entry_target = add_input(frame_input, "🎯 Target Price (₹):")
entry_risk_perc = add_input(frame_input, "⚠️ Risk % (e.g. 2):")
entry_reward_ratio = add_input(frame_input, "💹 Reward Ratio (e.g. 2):")
entry_position_size = add_input(frame_input, "🔢 Manual Position Size:")

tk.Button(frame_input, text="📈 Calculate Trade Plan", command=calculate, font=font_bold, bg="#4CAF50", fg="white").pack(pady=15, fill="x")

# --- Chart ---
fig, ax = plt.subplots(figsize=(4.5, 4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=frame_chart)
canvas.get_tk_widget().pack(expand=True, fill="both")

# --- Position Size Mini Calculator ---
tk.Label(frame_calc, text="🧮 Position Size Calculator", font=font_bold).pack(pady=5)
entry_calc_capital = add_input(frame_calc, "Capital (₹):")
entry_calc_entry = add_input(frame_calc, "Entry Price (₹):")
entry_calc_stop = add_input(frame_calc, "Stop-Loss Price (₹):")
entry_calc_risk = add_input(frame_calc, "Risk % (e.g. 2):")
tk.Button(frame_calc, text="🧾 Calculate Position Size", command=calculate_position_size, font=font_bold, bg="#2196F3", fg="white").pack(pady=10, fill="x")

result_position_calc = scrolledtext.ScrolledText(frame_calc, font=font_output, width=30, height=6, state='disabled')
result_position_calc.pack(fill="both", expand=True)

root.mainloop()
