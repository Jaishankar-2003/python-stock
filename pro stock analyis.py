import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Analyze function with enhanced logic
def analyze_trade():
    try:
        score = 0
        explanations = []

        # Get user inputs
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

        # Technical scoring (higher weight)
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

        # Additional scoring
        if chart_pattern == "Breakout":
            score += 1.5
            explanations.append("Breakout Chart Pattern")
        elif chart_pattern == "Consolidation":
            score += 1
            explanations.append("Consolidation Phase")
        elif chart_pattern == "Reversal":
            score += 0.5
            explanations.append("Reversal Setup")

        if sector_trend == "Yes":
            score += 1
            explanations.append("Sector is Trending")

        # Sentiment and advice
        if score >= 8:
            sentiment = "Strong Bullish"
            advice = "Ideal setup for swing trade. Consider entering with stop loss and defined targets."
        elif 6 <= score < 8:
            sentiment = "Moderate Bullish"
            advice = "Decent potential. Monitor price action and wait for confirmation."
        elif 4 <= score < 6:
            sentiment = "Cautious"
            advice = "Some signs of momentum. Wait for clearer signals."
        else:
            sentiment = "Bearish"
            advice = "Not suitable for swing trading at the moment."

        # Display results
        result_output.config(state="normal")
        result_output.delete(1.0, tk.END)
        result_output.insert(tk.END, f"Stock: {stock}\n")
        result_output.insert(tk.END, f"Sentiment: {sentiment}\n")
        result_output.insert(tk.END, f"Advice: {advice}\n\nExplanation:\n" + "\n".join(explanations))
        result_output.config(state="disabled")

        # Save trade if sentiment is Bullish
        if sentiment in ["Strong Bullish", "Moderate Bullish"]:
            trade_table.insert("", "end", values=(stock, sentiment, advice, datetime.now().strftime("%Y-%m-%d")))

    except ValueError:
        result_output.config(state="normal")
        result_output.delete(1.0, tk.END)
        result_output.insert(tk.END, "Please enter valid numeric values.")
        result_output.config(state="disabled")


# GUI setup
root = tk.Tk()
root.title("Advanced Swing Trade Analyzer")
root.geometry("1000x650")

# Input Frame
input_frame = tk.LabelFrame(root, text="Stock Input", padx=10, pady=10)
input_frame.pack(fill="x", padx=10, pady=5)

# Stock Name
tk.Label(input_frame, text="Stock Name:").grid(row=0, column=0, sticky="w")
stock_entry = tk.Entry(input_frame)
stock_entry.grid(row=0, column=1)

# Fundamental Inputs
tk.Label(input_frame, text="Revenue Growth %:").grid(row=1, column=0, sticky="w")
revenue_entry = tk.Entry(input_frame)
revenue_entry.grid(row=1, column=1)

tk.Label(input_frame, text="EPS Growth %:").grid(row=2, column=0, sticky="w")
eps_entry = tk.Entry(input_frame)
eps_entry.grid(row=2, column=1)

tk.Label(input_frame, text="Debt to Equity:").grid(row=3, column=0, sticky="w")
debt_entry = tk.Entry(input_frame)
debt_entry.grid(row=3, column=1)

tk.Label(input_frame, text="ROE %:").grid(row=4, column=0, sticky="w")
roe_entry = tk.Entry(input_frame)
roe_entry.grid(row=4, column=1)

# Technical Inputs
tk.Label(input_frame, text="EMA Crossover:").grid(row=1, column=2)
ema_var = ttk.Combobox(input_frame, values=["Yes", "No"])
ema_var.grid(row=1, column=3)

tk.Label(input_frame, text="RSI Value:").grid(row=2, column=2)
rsi_entry = tk.Entry(input_frame)
rsi_entry.grid(row=2, column=3)

tk.Label(input_frame, text="MACD Signal:").grid(row=3, column=2)
macd_var = ttk.Combobox(input_frame, values=["Bullish", "Bearish"])
macd_var.grid(row=3, column=3)

tk.Label(input_frame, text="Volume Spike:").grid(row=4, column=2)
volume_var = ttk.Combobox(input_frame, values=["Yes", "No"])
volume_var.grid(row=4, column=3)

# Additional Inputs
tk.Label(input_frame, text="Chart Pattern:").grid(row=5, column=0)
pattern_var = ttk.Combobox(input_frame, values=["None", "Breakout", "Consolidation", "Reversal"])
pattern_var.grid(row=5, column=1)

tk.Label(input_frame, text="Sector Trending:").grid(row=5, column=2)
sector_var = ttk.Combobox(input_frame, values=["Yes", "No"])
sector_var.grid(row=5, column=3)

# Analyze Button
analyze_btn = tk.Button(root, text="Analyze Trade", command=analyze_trade, bg="green", fg="white")
analyze_btn.pack(pady=10)

# Result Frame
result_frame = tk.LabelFrame(root, text="Analysis Result & Advice", padx=10, pady=10)
result_frame.pack(fill="x", padx=10, pady=5)

result_output = tk.Text(result_frame, height=10, state="disabled", bg="#f0f0f0", wrap="word")
result_output.pack(fill="x")

# Trade Table Frame
table_frame = tk.LabelFrame(root, text="Saved Swing Trades")
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

trade_table = ttk.Treeview(table_frame, columns=("Stock", "Sentiment", "Advice", "Date"), show="headings")
for col in ("Stock", "Sentiment", "Advice", "Date"):
    trade_table.heading(col, text=col)
    trade_table.column(col, anchor="center")

trade_table.pack(fill="both", expand=True)

root.mainloop()