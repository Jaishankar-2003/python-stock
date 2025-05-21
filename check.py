from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import tkinter.font as tkfont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import csv
import math

# --- Trade calculation function with duration-based CAGR ---
def general_trade_calculator(
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

    daily_gain = (target_price / entry_price) ** (1 / trade_duration) - 1 if trade_duration else None
    cagr = ((target_price / entry_price) ** (365 / trade_duration) - 1) * 100 if trade_duration else None

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
        "Daily Gain %": round(daily_gain * 100, 2) if daily_gain else "N/A",
        "Estimated CAGR %": round(cagr, 2) if cagr else "N/A"
    }

# --- GUI Setup ---
root = tk.Tk()
root.title("📈 Enhanced Swing Trade Calculator")
root.state("zoomed")

# Fonts
font_label = tkfont.Font(family="Arial", size=14)
font_entry = tkfont.Font(family="Arial", size=14)
font_output = tkfont.Font(family="Consolas", size=14)
font_bold = tkfont.Font(family="Arial", size=18, weight="bold")

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

# --- Chart Setup ---
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

# --- Inputs ---
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

# --- Output Display ---
output_text = scrolledtext.ScrolledText(frame_output, font=font_output, height=20)
output_text.pack(expand=True, fill="both")
frame_history.pack(fill="both", expand=True)

# Configure tags for styling output text
output_text.tag_configure("title", font=font_bold, foreground="#0B3D91")  # dark blue bold title
output_text.tag_configure("price", font=font_bold, foreground="#D35400")  # orange bold for prices
output_text.tag_configure("gain_positive", font=font_bold, foreground="#27AE60")  # green bold for positive gains
output_text.tag_configure("gain_negative", font=font_bold, foreground="#C0392B")  # red bold for negative gains
output_text.tag_configure("gain_neutral", font=font_bold, foreground="#7F8C8D")  # gray for neutral/unknown

# --- Trade History ---
history_text = scrolledtext.ScrolledText(frame_history, font=font_output, height=10, state='normal')
history_text.pack(fill="both", expand=True)
history_text.insert(tk.END, "📚 Trade Plan History:\n\n")

# --- Button Handlers ---
def calculate():
    try:
        result = general_trade_calculator(
            capital=float(entry_capital.get()),
            entry_price=float(entry_entry.get()),
            stop_loss_price=float(entry_stop_loss.get()) if entry_stop_loss.get() else None,
            target_price=float(entry_target.get()) if entry_target.get() else None,
            risk_perc=float(entry_risk_perc.get()) if entry_risk_perc.get() else None,
            reward_ratio=float(entry_reward_ratio.get()) if entry_reward_ratio.get() else None,
            manual_position_size=int(entry_position_size.get()) if entry_position_size.get() else None,
            trade_duration=int(entry_trade_duration.get()) if entry_trade_duration.get() else None
        )

        output_text.config(state='normal')
        output_text.delete("1.0", tk.END)

        # Clear previous tags (optional)
        for tag in output_text.tag_names():
            output_text.tag_delete(tag)

        # Re-add tags after clearing
        output_text.tag_configure("title", font=font_bold, foreground="#0B3D91")  # dark blue bold title
        output_text.tag_configure("price", font=font_bold, foreground="#D35400")  # orange bold for prices
        output_text.tag_configure("gain_positive", font=font_bold, foreground="#27AE60")  # green bold for positive gains
        output_text.tag_configure("gain_negative", font=font_bold, foreground="#C0392B")  # red bold for negative gains
        output_text.tag_configure("gain_neutral", font=font_bold, foreground="#7F8C8D")  # gray for neutral/unknown

        if isinstance(result, dict):
            output_text.insert(tk.END, "📊 Trade Plan Result:\n\n", "title")

            for key, value in result.items():
                line = f"{key}: {value}\n"
                if key in ["Entry Price", "Stop-Loss Price", "Target Price"]:
                    output_text.insert(tk.END, line, "price")
                elif key in ["Expected % Gain", "Estimated CAGR %"]:
                    try:
                        val_float = float(value)
                        if val_float > 0:
                            output_text.insert(tk.END, line, "gain_positive")
                        else:
                            output_text.insert(tk.END, line, "gain_negative")
                    except:
                        output_text.insert(tk.END, line, "gain_neutral")
                else:
                    output_text.insert(tk.END, line)

            # Append trade plan summary to history
            history_text.insert(tk.END, f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n")
            history_text.insert(tk.END, f"{result['Entry Price']} ➡ {result['Target Price']} | Gain: {result['Expected % Gain']}% | CAGR: {result['Estimated CAGR %']}%\n\n")
            update_chart(result["Entry Price"], result["Stop-Loss Price"], result["Target Price"])
        else:
            output_text.insert(tk.END, result)
            clear_chart()

        output_text.config(state='disabled')

    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

def reset_fields():
    for entry in [entry_capital, entry_entry, entry_stop_loss, entry_target,
                  entry_risk_perc, entry_reward_ratio, entry_position_size, entry_trade_duration]:
        entry.delete(0, tk.END)
    output_text.config(state='normal')
    output_text.delete("1.0", tk.END)
    output_text.config(state='disabled')
    clear_chart()

def export_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv")
    if not file_path:
        return
    try:
        content = output_text.get("1.0", tk.END).strip().splitlines()
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            for line in content:
                if ": " in line:
                    key, value = line.split(": ")
                    writer.writerow([key, value])
        messagebox.showinfo("Success", f"Exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

# --- Buttons ---
tk.Button(frame_input, text="📈 Calculate", font=font_bold, command=calculate, bg="#4CAF50", fg="white").pack(pady=10, fill="x")
tk.Button(frame_input, text="♻️ Reset", font=font_bold, command=reset_fields, bg="#FF9800", fg="white").pack(pady=5, fill="x")
tk.Button(frame_input, text="💾 Export to CSV", font=font_bold, command=export_csv, bg="#2196F3", fg="white").pack(pady=5, fill="x")

root.mainloop()
