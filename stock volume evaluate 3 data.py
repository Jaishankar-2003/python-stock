import tkinter as tk
from tkinter import messagebox
import re

def extract_float(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        value = match.group(1).replace(",", "").strip()
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0

def extract_percent(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1).strip())
        except ValueError:
            return 0.0
    return 0.0

def extract_string(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def extract_data_from_text(text):
    return {
        "volume": extract_float(text, r"Traded Volume .*?([\d,.]+)"),
        "value": extract_float(text, r"Traded Value .*?([\d,.]+)"),
        "cap": extract_float(text, r"Total Market Cap .*?([\d,.]+)"),
        "float_cap": extract_float(text, r"Free Float Market Cap .*?([\d,.]+)"),
        "impact": extract_float(text, r"Impact cost\s*([\d.]+)"),
        "delivery": extract_percent(text, r"Deliverable / Traded\s+Quantity\s+([\d.]+)\s*%"),
        "margin": extract_float(text, r"Applicable Margin Rate\s*([\d.]+)"),
        "daily_vol": extract_float(text, r"Daily Volatility\s*([\d.]+)"),
        "annual_vol": extract_float(text, r"Annualised Volatility\s*([\d.]+)"),
        "pe": extract_float(text, r"Adjusted P/E\s*([\d.]+)"),
        "low52": extract_float(text, r"52 Week Low.*?([\d.]+)"),
        "high52": extract_float(text, r"52 Week High.*?([\d.]+)"),
        "index": extract_string(text, r"Index\s+(.*?)\n")
    }

def populate_fields():
    try:
        data = extract_data_from_text(input_box.get("1.0", tk.END))
        entry_volume.delete(0, tk.END)
        entry_volume.insert(0, data["volume"])
        entry_value.delete(0, tk.END)
        entry_value.insert(0, data["value"])
        entry_cap.delete(0, tk.END)
        entry_cap.insert(0, data["cap"])
        entry_float_cap.delete(0, tk.END)
        entry_float_cap.insert(0, data["float_cap"])
        entry_impact.delete(0, tk.END)
        entry_impact.insert(0, data["impact"])
        entry_delivery.delete(0, tk.END)
        entry_delivery.insert(0, data["delivery"])
        entry_margin.delete(0, tk.END)
        entry_margin.insert(0, data["margin"])
        entry_daily_vol.delete(0, tk.END)
        entry_daily_vol.insert(0, data["daily_vol"])
        entry_annual_vol.delete(0, tk.END)
        entry_annual_vol.insert(0, data["annual_vol"])
        entry_pe.delete(0, tk.END)
        entry_pe.insert(0, data["pe"])
        entry_52low.delete(0, tk.END)
        entry_52low.insert(0, data["low52"])
        entry_52high.delete(0, tk.END)
        entry_52high.insert(0, data["high52"])
        entry_index.delete(0, tk.END)
        entry_index.insert(0, data["index"])
    except Exception as e:
        messagebox.showerror("Parse Error", f"Error parsing data: {str(e)}")

def get_market_cap_segment(market_cap):
    if market_cap < 5000:
        return "Small Cap"
    elif 5000 <= market_cap <= 20000:
        return "Mid Cap"
    else:
        return "Large Cap"

def evaluate_stock():
    try:
        volume = float(entry_volume.get())
        value = float(entry_value.get())
        cap = float(entry_cap.get())
        float_cap = float(entry_float_cap.get())
        impact_cost = float(entry_impact.get())
        deliverable_pct = float(entry_delivery.get())
        margin = float(entry_margin.get())
        daily_vol = float(entry_daily_vol.get())
        annual_vol = float(entry_annual_vol.get())
        pe_ratio = float(entry_pe.get())
        low52 = float(entry_52low.get())
        high52 = float(entry_52high.get())
        index = entry_index.get()

        segment = get_market_cap_segment(cap)
        high_score = 0
        good_score = 0

        if segment == "Small Cap":
            vol_th = (5, 20)
            val_th = (100, 300)
        elif segment == "Mid Cap":
            vol_th = (10, 50)
            val_th = (300, 800)
        else:
            vol_th = (20, 100)
            val_th = (500, 2000)

        if volume > vol_th[1]:
            high_score += 1
        elif volume >= vol_th[0]:
            good_score += 1

        if value > val_th[1]:
            high_score += 1
        elif value >= val_th[0]:
            good_score += 1

        if cap > 20000:
            high_score += 1
        elif cap >= 5000:
            good_score += 1

        if high_score == 3:
            result = f"🔥 High Recommend ({segment})"
            color = "green"
        elif high_score >= 2 or (high_score == 1 and good_score >= 2):
            result = f"✅ Good ({segment})"
            color = "orange"
        else:
            result = f"❌ Bad ({segment})"
            color = "red"

        tags = []
        if cap != 0 and abs(cap - float_cap) / cap < 0.01:
            tags.append("✅ Public Float Healthy")
        if impact_cost < 0.1:
            tags.append("✅ Low Impact Cost")
        else:
            tags.append("⚠️ High Impact Cost")
        if deliverable_pct >= 25:
            tags.append("✅ Strong Delivery")
        else:
            tags.append("⚠️ Low Delivery %")
        if margin <= 40:
            tags.append("✅ Margin OK")
        if 2 <= daily_vol <= 5:
            tags.append("✅ Volatility OK")
        elif daily_vol > 6:
            tags.append("❌ Too Volatile")
        if 40 <= annual_vol <= 90:
            tags.append("✅ Swing Range Volatility")
        if pe_ratio > 80:
            tags.append("⚠️ High P/E")
        tags.append(f"Index: {index}")
        tags.append(f"52W Range: ₹{low52} - ₹{high52}")

        label_result.config(text=f"Recommendation: {result}", fg=color)
        label_tags.config(text="\n".join(tags), fg="blue")

    except ValueError:
        messagebox.showerror("Input Error", "Enter valid numeric values.")

# GUI Setup
root = tk.Tk()
root.title("Swing Trade Evaluator (Auto-Parse Enabled)")

fields = [
    ("Traded Volume (Lakhs):", "entry_volume"),
    ("Traded Value (₹ Cr.):", "entry_value"),
    ("Market Cap (₹ Cr.):", "entry_cap"),
    ("Free Float Cap (₹ Cr.):", "entry_float_cap"),
    ("Impact Cost:", "entry_impact"),
    ("% Deliverable Quantity:", "entry_delivery"),
    ("Applicable Margin Rate:", "entry_margin"),
    ("Daily Volatility (%):", "entry_daily_vol"),
    ("Annualised Volatility (%):", "entry_annual_vol"),
    ("P/E Ratio:", "entry_pe"),
    ("52W Low Price:", "entry_52low"),
    ("52W High Price:", "entry_52high"),
    ("Index Name:", "entry_index"),
]

entries = {}
for i, (label_text, var_name) in enumerate(fields):
    tk.Label(root, text=label_text).grid(row=i, column=0, padx=10, pady=2, sticky="e")
    entry = tk.Entry(root)
    entry.grid(row=i, column=1, padx=10, pady=2)
    entries[var_name] = entry

entry_volume = entries["entry_volume"]
entry_value = entries["entry_value"]
entry_cap = entries["entry_cap"]
entry_float_cap = entries["entry_float_cap"]
entry_impact = entries["entry_impact"]
entry_delivery = entries["entry_delivery"]
entry_margin = entries["entry_margin"]
entry_daily_vol = entries["entry_daily_vol"]
entry_annual_vol = entries["entry_annual_vol"]
entry_pe = entries["entry_pe"]
entry_52low = entries["entry_52low"]
entry_52high = entries["entry_52high"]
entry_index = entries["entry_index"]

# Buttons
tk.Button(root, text="Evaluate", command=evaluate_stock).grid(row=len(fields), column=0, columnspan=2, pady=5)
tk.Button(root, text="📥 Auto-Fill From Raw Data", command=populate_fields).grid(row=len(fields)+1, column=0, columnspan=2, pady=5)

# Output Labels
label_result = tk.Label(root, text="", font=("Arial", 13, "bold"))
label_result.grid(row=len(fields)+2, column=0, columnspan=2, pady=5)

label_tags = tk.Label(root, text="", font=("Arial", 10), justify="left")
label_tags.grid(row=len(fields)+3, column=0, columnspan=2, pady=5)

# Input Text Box
tk.Label(root, text="Paste Raw Data Below:").grid(row=len(fields)+4, column=0, columnspan=2)
input_box = tk.Text(root, height=12, width=50)
input_box.grid(row=len(fields)+5, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
