import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Main analysis logic
def analyze_trade():
    try:
        score = 0
        explanations = []

        stock = stock_entry.get().strip()
        revenue_growth = float(revenue_entry.get())
        eps_growth = float(eps_entry.get())
        debt_equity = float(debt_entry.get())
        roe = float(roe_entry.get())
        ema_crossover = ema_var.get()
        rsi = int(rsi_entry.get())
        macd = macd_var.get()
        volume_spike = volume_var.get()
        chart_pattern = pattern_var.get()
        sector_trend = sector_var.get()

        # Fundamental scoring
        if revenue_growth > 10:
            score += 0.5
            explanations.append("Revenue Growth > 10%")
        if eps_growth > 10:
            score += 0.5
            explanations.append("EPS Growth > 10%")
        if debt_equity < 1:
            score += 0.5
            explanations.append("Low Debt-Equity Ratio")
        if roe > 12:
            score += 0.5
            explanations.append("ROE > 12%")

        # Technical scoring
        if ema_crossover == "Yes":
            score += 2
            explanations.append("Bullish EMA Crossover")
        if 40 < rsi < 70:
            score += 1.5
            explanations.append("RSI in Bullish Zone (40–70)")
        if macd == "Bullish":
            score += 1.5
            explanations.append("MACD is Bullish")
        if volume_spike == "Yes":
            score += 1
            explanations.append("Volume Spike Confirmed")

        # Chart pattern
        if chart_pattern == "Breakout":
            score += 1.5
            explanations.append("Breakout Pattern")
        elif chart_pattern == "Consolidation":
            score += 1
            explanations.append("Consolidation Phase")
        elif chart_pattern == "Reversal":
            score += 0.5
            explanations.append("Reversal Setup")

        if sector_trend == "Yes":
            score += 1
            explanations.append("Sector is Trending")

        # Sentiment logic
        if score >= 8:
            sentiment = "Strong Bullish"
            advice = "Ideal setup. Use stop loss and define targets."
        elif 6 <= score < 8:
            sentiment = "Moderate Bullish"
            advice = "Decent potential. Monitor price action closely."
        elif 4 <= score < 6:
            sentiment = "Cautious"
            advice = "Some signs of momentum. Wait for clearer signal."
        else:
            sentiment = "Bearish"
            advice = "Not suitable for swing trade currently."

        result_output.config(state="normal")
        result_output.delete("1.0", tk.END)
        result_output.insert(tk.END, f"Stock: {stock}\nSentiment: {sentiment}\nAdvice: {advice}\n\nDetails:\n" + "\n".join(explanations))
        result_output.config(state="disabled")

        if sentiment in ["Strong Bullish", "Moderate Bullish"]:
            trade_table.insert("", "end", values=(stock, sentiment, advice, datetime.now().strftime("%Y-%m-%d")))

    except ValueError:
        result_output.config(state="normal")
        result_output.delete("1.0", tk.END)
        result_output.insert(tk.END, "Invalid input. Please enter numeric values.")
        result_output.config(state="disabled")


# --- GUI Setup ---
root = tk.Tk()
root.title("Advanced Swing Trade Analyzer")
root.geometry("1020x700")
root.configure(bg="#f9f9f9")

style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

# Input Frame
input_frame = tk.LabelFrame(root, text="Trade Input Parameters", font=("Segoe UI", 12, "bold"), bg="#e9f1ff", padx=10, pady=10)
input_frame.pack(fill="x", padx=10, pady=10)

labels = [
    ("Stock Name:", 0, 0), ("Revenue Growth %:", 1, 0), ("EPS Growth %:", 2, 0),
    ("Debt to Equity:", 3, 0), ("ROE %:", 4, 0), ("EMA Crossover:", 1, 2),
    ("RSI Value:", 2, 2), ("MACD Signal:", 3, 2), ("Volume Spike:", 4, 2),
    ("Chart Pattern:", 5, 0), ("Sector Trending:", 5, 2)
]

for text, row, col in labels:
    tk.Label(input_frame, text=text, bg="#e9f1ff").grid(row=row, column=col, sticky="w", padx=5, pady=4)

# Entries
stock_entry = tk.Entry(input_frame); stock_entry.grid(row=0, column=1)
revenue_entry = tk.Entry(input_frame); revenue_entry.grid(row=1, column=1)
eps_entry = tk.Entry(input_frame); eps_entry.grid(row=2, column=1)
debt_entry = tk.Entry(input_frame); debt_entry.grid(row=3, column=1)
roe_entry = tk.Entry(input_frame); roe_entry.grid(row=4, column=1)
rsi_entry = tk.Entry(input_frame); rsi_entry.grid(row=2, column=3)

# Comboboxes
ema_var = ttk.Combobox(input_frame, values=["Yes", "No"], state="readonly"); ema_var.grid(row=1, column=3)
macd_var = ttk.Combobox(input_frame, values=["Bullish", "Bearish"], state="readonly"); macd_var.grid(row=3, column=3)
volume_var = ttk.Combobox(input_frame, values=["Yes", "No"], state="readonly"); volume_var.grid(row=4, column=3)
pattern_var = ttk.Combobox(input_frame, values=["None", "Breakout", "Consolidation", "Reversal"], state="readonly"); pattern_var.grid(row=5, column=1)
sector_var = ttk.Combobox(input_frame, values=["Yes", "No"], state="readonly"); sector_var.grid(row=5, column=3)

# Analyze Button
analyze_btn = tk.Button(root, text="Analyze Trade", bg="dark green", fg="white", command=analyze_trade)
analyze_btn.pack(pady=10)

# Result Frame
result_frame = tk.LabelFrame(root, text="Analysis Output", font=("Segoe UI", 12, "bold"), padx=10, pady=10)
result_frame.pack(fill="x", padx=10)

result_output = tk.Text(result_frame, height=10, state="disabled", bg="#f4f4f4", wrap="word", font=("Segoe UI", 10))
result_output.pack(fill="x")

# Trade Table
table_frame = tk.LabelFrame(root, text="Saved Swing Trades", font=("Segoe UI", 12, "bold"))
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

trade_table = ttk.Treeview(table_frame, columns=("Stock", "Sentiment", "Advice", "Date"), show="headings", height=8)
for col in ("Stock", "Sentiment", "Advice", "Date"):
    trade_table.heading(col, text=col)
    trade_table.column(col, anchor="center", stretch=True)

trade_table.pack(fill="both", expand=True)

root.mainloop()
