import tkinter as tk
from tkinter import messagebox


def analyze_stock():
    try:
        # Get inputs
        market_cap = float(entry_market_cap.get())
        roe = float(entry_roe.get())
        profit_growth = float(entry_profit_growth.get())
        yoy_profit_growth = float(entry_yoy_profit_growth.get())
        debt_to_equity = float(entry_debt_to_equity.get())
        ocf_gt_np = var_ocf_gt_np.get()
        net_profit_percent = float(entry_net_profit_percent.get())
        pe_ratio = float(entry_pe_ratio.get())
        roce = float(entry_roce.get())
        profit_growth_3yr = float(entry_profit_growth_3yr.get())
        eps = float(entry_eps.get())

        # Condition Checks
        conditions = {
            "Market Cap > 5000": market_cap > 5000,
            "ROE > 12%": roe > 12,
            "Profit Growth > 10%": profit_growth > 10,
            "YOY Profit Growth > 10%": yoy_profit_growth > 10,
            "Debt/Equity < 0.5": debt_to_equity < 0.5,
            "OCF > Net Profit (3Y)": ocf_gt_np == 1,
            "Net Profit % > 10": net_profit_percent > 10,
            "P/E < 30": pe_ratio < 30,
            "ROCE > 15%": roce > 15,
            "3Y Profit Growth > 10": profit_growth_3yr > 10,
            "EPS > 3": eps > 3
        }

        # Calculate result
        passed = [k for k, v in conditions.items() if v]
        score = len(passed) / len(conditions) * 100

        # Show result
        result_text.delete("1.0", tk.END)
        for k in conditions:
            result_text.insert(tk.END, f"{k}: {'✅' if conditions[k] else '❌'}\n")

        result_text.insert(tk.END, f"\nScore: {score:.2f}%\n")

        if score >= 80:
            result_text.insert(tk.END, "🟢 Verdict: Strong Candidate for Swing Trade\n")
            valid_listbox.insert(tk.END, f"{entry_stock_name.get()} ({score:.2f}%)")
        elif score >= 60:
            result_text.insert(tk.END, "🟡 Verdict: Moderate Candidate\n")
        else:
            result_text.insert(tk.END, "🔴 Verdict: Weak Candidate\n")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values for all fields.")


# Tkinter window
root = tk.Tk()
root.title("Swing Trade Stock Selector")

tk.Label(root, text="Stock Name").grid(row=0, column=0)
entry_stock_name = tk.Entry(root)
entry_stock_name.grid(row=0, column=1)

labels = [
    "Market Cap (in Cr)",
    "Return on Equity (%)",
    "Profit Growth (%)",
    "YOY Profit Growth (%)",
    "Debt to Equity",
    "OCF > Net Profit (3Y) [1=True, 0=False]",
    "Net Profit % of Revenue",
    "P/E Ratio",
    "ROCE (%)",
    "Profit Growth (3Y) (%)",
    "EPS (Latest Quarter)"
]

entries = []
for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i + 1, column=0)
    if "OCF" in label:
        var_ocf_gt_np = tk.IntVar()
        entry = tk.Entry(root, textvariable=var_ocf_gt_np)
    else:
        entry = tk.Entry(root)
    entry.grid(row=i + 1, column=1)
    entries.append(entry)

(entry_market_cap, entry_roe, entry_profit_growth, entry_yoy_profit_growth, entry_debt_to_equity,
 _, entry_net_profit_percent, entry_pe_ratio, entry_roce, entry_profit_growth_3yr, entry_eps) = entries

tk.Button(root, text="Analyze", command=analyze_stock).grid(row=13, column=0, columnspan=2, pady=10)

tk.Label(root, text="Analysis Result").grid(row=14, column=0, columnspan=2)
result_text = tk.Text(root, height=12, width=50)
result_text.grid(row=15, column=0, columnspan=2)

tk.Label(root, text="Valid Stocks").grid(row=0, column=3)
valid_listbox = tk.Listbox(root, height=20, width=30)
valid_listbox.grid(row=1, column=3, rowspan=15)

root.mainloop()
