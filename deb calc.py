import tkinter as tk
from tkinter import messagebox

def calculate_debt_percent():
    try:
        market_cap = float(entry_market_cap.get())
        total_debt = float(entry_debt.get())

        if market_cap <= 0:
            raise ValueError("Market cap must be positive")

        debt_percent = (total_debt / market_cap) * 100
        result_label.config(text=f"Debt is {debt_percent:.2f}% of Market Cap")

        # Interpretation for Swing Trading
        if debt_percent < 30:
            interpretation_label.config(
                text="🟢 Low Debt - Strong candidate for swing trading.",
                fg="green"
            )
        elif 30 <= debt_percent <= 70:
            interpretation_label.config(
                text="🟡 Moderate Debt - Be cautious and check fundamentals.",
                fg="orange"
            )
        else:
            interpretation_label.config(
                text="🔴 High Debt - Risky for swing trading.",
                fg="red"
            )
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

def clear_fields():
    entry_market_cap.delete(0, tk.END)
    entry_debt.delete(0, tk.END)
    result_label.config(text="")
    interpretation_label.config(text="")

# Main window
root = tk.Tk()
root.title("Swing Trade Debt Analyzer")
root.geometry("450x300")
root.configure(bg="#f4f4f4")

# Title
tk.Label(root, text="💹 Swing Trader's Debt Analyzer", font=("Helvetica", 16, "bold"), bg="#f4f4f4", fg="#333").pack(pady=10)

# Market Cap Input
tk.Label(root, text="Market Cap (in ₹ Cr):", bg="#f4f4f4").pack()
entry_market_cap = tk.Entry(root, width=30)
entry_market_cap.pack()

# Debt Input
tk.Label(root, text="Total Debt (in ₹ Cr):", bg="#f4f4f4").pack(pady=(10, 0))
entry_debt = tk.Entry(root, width=30)
entry_debt.pack()

# Buttons
button_frame = tk.Frame(root, bg="#f4f4f4")
button_frame.pack(pady=15)
tk.Button(button_frame, text="Calculate", command=calculate_debt_percent, bg="#2196F3", fg="white", width=10).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Clear", command=clear_fields, width=10).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Exit", command=root.quit, bg="#f44336", fg="white", width=10).grid(row=0, column=2, padx=5)

# Result and interpretation
result_label = tk.Label(root, text="", font=("Arial", 12, "bold"), bg="#f4f4f4")
result_label.pack(pady=(5, 0))

interpretation_label = tk.Label(root, text="", font=("Arial", 12), bg="#f4f4f4")
interpretation_label.pack()

# Run the GUI loop
root.mainloop()
