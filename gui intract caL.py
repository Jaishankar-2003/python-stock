import tkinter as tk
from tkinter import messagebox, scrolledtext


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

    # Calculate risk per share
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

    # Risk amount
    risk_amount = capital * (risk_perc / 100) if risk_perc else risk_per_share * (capital // entry_price)

    # Position size: manual if given, else auto calculate
    if manual_position_size is not None and manual_position_size > 0:
        position_size = int(manual_position_size)
        invested_amount = position_size * entry_price
        # Recalculate risk amount based on manual position size
        risk_amount = position_size * risk_per_share
    else:
        position_size = int(risk_amount // risk_per_share)
        invested_amount = position_size * entry_price

    # Reward/Target price
    if reward_ratio and not target_price:
        reward_per_share = risk_per_share * reward_ratio
        target_price = entry_price + reward_per_share
    elif target_price:
        reward_per_share = target_price - entry_price
        reward_ratio = reward_per_share / risk_per_share
    else:
        return "❌ Either Target Price or Reward Ratio is required."

    # Profit and % gain
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


def calculate():
    try:
        capital = float(entry_capital.get())
        entry = float(entry_entry.get())
        stop_loss = float(entry_stop_loss.get()) if entry_stop_loss.get() else None
        target = float(entry_target.get()) if entry_target.get() else None
        risk_perc = float(entry_risk_perc.get()) if entry_risk_perc.get() else None
        reward_ratio = float(entry_reward_ratio.get()) if entry_reward_ratio.get() else None
        manual_pos = int(entry_manual_pos.get()) if entry_manual_pos.get() else None

        result = general_trade_calculator(
            capital=capital,
            entry_price=entry,
            stop_loss_price=stop_loss,
            target_price=target,
            risk_perc=risk_perc,
            reward_ratio=reward_ratio,
            manual_position_size=manual_pos
        )

        output_text.config(state='normal')
        output_text.delete("1.0", tk.END)

        if isinstance(result, dict):
            output_text.insert(tk.END, "📊 Trade Plan Summary:\n\n")
            for key, value in result.items():
                start = output_text.index(tk.END)
                output_text.insert(tk.END, f"{key}: {value}\n")
                end = output_text.index(tk.END)

                # Apply highlight tags
                if "Risk" in key:
                    output_text.tag_add("risk", start, end)
                elif "Stop-Loss" in key:
                    output_text.tag_add("stop", start, end)
                elif "Expected Profit" in key:
                    output_text.tag_add("profit", start, end)
                elif "Expected % Gain" in key:
                    output_text.tag_add("gain", start, end)
        else:
            output_text.insert(tk.END, result)

        output_text.config(state='disabled')

    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")


# Build GUI
root = tk.Tk()
root.title("Swing Trade Calculator 🧮")
root.geometry("600x650")

tk.Label(root, text="Total Capital (₹):").pack()
entry_capital = tk.Entry(root)
entry_capital.pack()

tk.Label(root, text="Entry Price (₹):").pack()
entry_entry = tk.Entry(root)
entry_entry.pack()

tk.Label(root, text="Stop Loss Price (₹):").pack()
entry_stop_loss = tk.Entry(root)
entry_stop_loss.pack()

tk.Label(root, text="Target Price (₹):").pack()
entry_target = tk.Entry(root)
entry_target.pack()

tk.Label(root, text="Risk % (e.g., 2.5):").pack()
entry_risk_perc = tk.Entry(root)
entry_risk_perc.pack()

tk.Label(root, text="Reward Ratio (e.g., 2.0):").pack()
entry_reward_ratio = tk.Entry(root)
entry_reward_ratio.pack()

tk.Label(root, text="Manual Position Size (optional):").pack()
entry_manual_pos = tk.Entry(root)
entry_manual_pos.pack()

tk.Button(root, text="Calculate", command=calculate, bg="green", fg="white").pack(pady=10)

output_text = scrolledtext.ScrolledText(root, height=22, width=70, wrap=tk.WORD)
output_text.pack()

output_text.tag_config("risk", foreground="red", font=('Arial', 10, 'bold'))
output_text.tag_config("profit", foreground="green", font=('Arial', 10, 'bold'))
output_text.tag_config("gain", foreground="blue", font=('Arial', 10, 'bold'))
output_text.tag_config("stop", foreground="darkorange", font=('Arial', 10, 'bold'))

root.mainloop()
