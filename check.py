from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import tkinter.font as tkfont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import csv

# --- Trade Calculator ---
def enhanced_trade_calculator(
    capital=None,
    entry_price=None,
    stop_loss_price=None,
    target_price=None,
    risk_perc=None,
    reward_ratio=None,
    manual_position_size=None,
    trade_duration=None
):
    if not capital or not entry_price:
        return "❌ Capital and Entry Price are required."

    if stop_loss_price is not None:
        risk_per_share = entry_price - stop_loss_price
        if risk_per_share <= 0:
            return "❌ Stop-loss must be below entry price."
    elif risk_perc and capital:
        risk_amount = capital * (risk_perc / 100)
        position_size_estimate = int(capital // entry_price) or 1
        risk_per_share = risk_amount / position_size_estimate
        stop_loss_price = entry_price - risk_per_share
    else:
        return "❌ Either Stop-Loss Price or Risk % is required."

    if manual_position_size:
        position_size = manual_position_size
        risk_amount = risk_per_share * position_size
    else:
        if risk_perc and capital:
            risk_amount = capital * (risk_perc / 100)
            position_size = int(risk_amount // risk_per_share)
        else:
            position_size = int(capital // entry_price)
            risk_amount = risk_per_share * position_size

    invested_amount = position_size * entry_price

    if reward_ratio and not target_price:
        reward_per_share = risk_per_share * reward_ratio
        target_price = entry_price + reward_per_share
    elif target_price:
        reward_per_share = target_price - entry_price
        reward_ratio = reward_per_share / risk_per_share if risk_per_share else 0
    else:
        return "❌ Either Target Price or Reward Ratio is required."

    expected_profit = reward_per_share * position_size
    percent_gain = (expected_profit / capital) * 100 if capital else 0
    break_even_price = entry_price + (risk_amount / position_size if position_size else 0)
    capital_usage_percent = (invested_amount / capital) * 100 if capital else 0
    risk_on_invested_percent = (risk_amount / invested_amount) * 100 if invested_amount else 0
    risk_adjusted_return = (reward_ratio / risk_on_invested_percent) * 100 if risk_on_invested_percent else 0

    if trade_duration and trade_duration > 0:
        daily_gain = (target_price / entry_price) ** (1 / trade_duration) - 1
        cagr = ((target_price / entry_price) ** (365 / trade_duration) - 1) * 100
        estimated_exit_date = datetime.today() + timedelta(days=trade_duration)
        reward_per_day = expected_profit / trade_duration
        risk_per_day = risk_amount / trade_duration
        profit_per_day = (expected_profit - risk_amount) / trade_duration
    else:
        daily_gain = cagr = reward_per_day = risk_per_day = profit_per_day = estimated_exit_date = None

    return {
        "Entry Price": round(entry_price, 2),
        "Stop-Loss Price": round(stop_loss_price, 2),
        "Target Price": round(target_price, 2),
        "Break-Even Price": round(break_even_price, 2),
        "Risk per Share": round(risk_per_share, 2),
        "Reward per Share": round(reward_per_share, 2),
        "Reward Ratio": round(reward_ratio, 2),
        "Risk Amount (₹)": round(risk_amount, 2),
        "Position Size": position_size,
        "Invested Amount (₹)": round(invested_amount, 2),
        "Capital Usage %": round(capital_usage_percent, 2),
        "Risk on Invested %": round(risk_on_invested_percent, 2),
        "Risk-Adjusted Return": round(risk_adjusted_return, 2),
        "Expected Profit (₹)": round(expected_profit, 2),
        "Expected % Gain": round(percent_gain, 2),
        "Profit per Day (₹)": round(profit_per_day, 2) if profit_per_day is not None else "N/A",
        "Risk per Day (₹)": round(risk_per_day, 2) if risk_per_day is not None else "N/A",
        "Reward per Day (₹)": round(reward_per_day, 2) if reward_per_day is not None else "N/A",
        "Daily Gain %": round(daily_gain * 100, 2) if daily_gain is not None else "N/A",
        "Estimated CAGR %": round(cagr, 2) if cagr is not None else "N/A",
        "Estimated Exit Date": estimated_exit_date.strftime("%Y-%m-%d") if estimated_exit_date else "N/A"
    }

# --- GUI ---
root = tk.Tk()
root.title("📈 Enhanced Swing Trade Calculator")
root.state("zoomed")

# Fonts
font_label = tkfont.Font(family="Arial", size=14)
font_entry = tkfont.Font(family="Arial", size=14)
font_output = tkfont.Font(family="Consolas", size=18)
font_bold = tkfont.Font(family="Arial", size=19, weight="bold")

# Frames
frame_input = tk.Frame(root, padx=10, pady=10)
frame_output = tk.Frame(root, padx=10, pady=10)
frame_chart = tk.Frame(root, padx=10, pady=10)
frame_history = tk.Frame(frame_output, pady=10)

frame_input.grid(row=0, column=0, sticky="nsew")
frame_output.grid(row=0, column=1, sticky="nsew")
frame_chart.grid(row=0, column=2, sticky="nsew")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_rowconfigure(0, weight=1)

# Chart
fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=frame_chart)
canvas.get_tk_widget().pack(expand=True, fill="both")

def update_chart(entry_price, stop_loss_price, target_price):
    ax.clear()
    ax.set_title("Trade Setup", fontsize=14)
    ax.set_ylabel("Price (₹)")
    ax.set_xticks([])
    prices = [stop_loss_price, entry_price, target_price]
    labels = ["Stop Loss", "Entry", "Target"]
    ax.plot([1, 2, 3], prices, marker='o', linestyle='-', color='blue')
    for i, (x, y) in enumerate(zip([1, 2, 3], prices)):
        ax.text(x, y, f"{labels[i]}:\n₹{y}", ha='center', va='bottom', fontweight='bold')
    canvas.draw()

def clear_chart():
    ax.clear()
    canvas.draw()

# Input fields helper
def add_input(parent, label):
    frame = tk.Frame(parent)
    frame.pack(fill="x", pady=4)
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
entry_trade_duration = add_input(frame_input, "⏱️ Trade Duration (Days):")

# Output Display
output_text = scrolledtext.ScrolledText(frame_output, font=font_output, height=20)
output_text.pack(expand=True, fill="both")
frame_history.pack(fill="both", expand=True)

output_text.tag_configure("title", font=font_bold, foreground="#0B3D91")
output_text.tag_configure("normal", font=font_output, foreground="black")
output_text.tag_configure("error", font=font_output, foreground="red")
output_text.tag_configure("green_text", font=font_output, foreground="green")
output_text.tag_configure("green", font=font_output, foreground="green")
output_text.tag_configure("red", font=font_output, foreground="red")
output_text.tag_configure("blue", font=font_output, foreground="blue")
output_text.tag_configure("orange", font=font_output, foreground="orange")
output_text.tag_configure("yellow", font=font_output, foreground="dark goldenrod")


# Trade History
trade_history = []

listbox_history = tk.Listbox(frame_history, height=6, font=font_label)
listbox_history.pack(side="left", fill="both", expand=True)

scrollbar_history = tk.Scrollbar(frame_history)
scrollbar_history.pack(side="right", fill="y")
listbox_history.config(yscrollcommand=scrollbar_history.set)
scrollbar_history.config(command=listbox_history.yview)

def update_history(trade_data):
    summary = (
        f"Entry: ₹{trade_data['Entry Price']} | "
        f"SL: ₹{trade_data['Stop-Loss Price']} | "
        f"Target: ₹{trade_data['Target Price']} | "
        f"Pos: {trade_data['Position Size']} | "
        f"Profit: ₹{trade_data['Expected Profit (₹)']}"
    )
    trade_history.append(trade_data)
    listbox_history.insert(tk.END, summary)

def on_history_select(event):
    index = event.widget.curselection()
    if index:
        display_output(trade_history[index[0]])

listbox_history.bind("<<ListboxSelect>>", on_history_select)

# Output Rendering
def clear_output():
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)

def display_output(results):
    clear_output()
    if isinstance(results, dict):
        output_text.insert(tk.END, "Enhanced Swing Trade Calculator Results\n", "title")
        output_text.insert(tk.END, "="*40 + "\n", "title")
        for k, v in results.items():
            if k == "Entry Price":
                output_text.insert(tk.END, f"{k}: {v}\n", "green_text")
            elif k in ["Expected Profit (₹)", "Reward Ratio", "Estimated CAGR %"]:
                output_text.insert(tk.END, f"{k}: {v}\n", "green")
            elif k in ["Stop-Loss Price", "Risk per Share", "Risk Amount (₹)", "Risk on Invested %"]:
                output_text.insert(tk.END, f"{k}: {v}\n", "red")
            elif k in ["Capital Usage %"]:
                output_text.insert(tk.END, f"{k}: {v}\n", "orange")
            elif k in ["Break-Even Price", "Invested Amount (₹)"]:
                output_text.insert(tk.END, f"{k}: {v}\n", "blue")
            else:
                output_text.insert(tk.END, f"{k}: {v}\n")
        update_chart(results["Entry Price"], results["Stop-Loss Price"], results["Target Price"])
    else:
        output_text.insert(tk.END, results, "error")
        clear_chart()
    output_text.config(state="disabled")

# Button Actions
def on_calculate():
    try:
        result = enhanced_trade_calculator(
            capital=float(entry_capital.get()),
            entry_price=float(entry_entry.get()),
            stop_loss_price=float(entry_stop_loss.get()) if entry_stop_loss.get() else None,
            target_price=float(entry_target.get()) if entry_target.get() else None,
            risk_perc=float(entry_risk_perc.get()) if entry_risk_perc.get() else None,
            reward_ratio=float(entry_reward_ratio.get()) if entry_reward_ratio.get() else None,
            manual_position_size=int(entry_position_size.get()) if entry_position_size.get() else None,
            trade_duration=int(entry_trade_duration.get()) if entry_trade_duration.get() else None
        )
        display_output(result)
        if isinstance(result, dict):
            update_history(result)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

def on_clear():
    for e in [entry_capital, entry_entry, entry_stop_loss, entry_target,
              entry_risk_perc, entry_reward_ratio, entry_position_size, entry_trade_duration]:
        e.delete(0, tk.END)
    clear_output()
    clear_chart()

def on_export():
    if not trade_history:
        messagebox.showinfo("No Data", "No trade data to export.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
    if not path:
        return
    try:
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(trade_history[0].keys())
            for trade in trade_history:
                writer.writerow(trade.values())
        messagebox.showinfo("Export", f"Exported to {path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Buttons
btn_frame = tk.Frame(frame_input, pady=10)
btn_frame.pack(fill="x")

tk.Button(btn_frame, text="Calculate", font=font_label, bg="#4CAF50", fg="white", command=on_calculate).pack(side="left", expand=True, fill="x", padx=5)
tk.Button(btn_frame, text="Clear", font=font_label, bg="#f44336", fg="white", command=on_clear).pack(side="left", expand=True, fill="x", padx=5)
tk.Button(btn_frame, text="Export History", font=font_label, bg="#2196F3", fg="white", command=on_export).pack(side="left", expand=True, fill="x", padx=5)

root.mainloop()
