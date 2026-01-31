# import tkinter as tk
# from tkinter import messagebox
# import re
#
# def extract_float(text, pattern):
#     match = re.search(pattern, text, re.IGNORECASE)
#     if match:
#         value = match.group(1).replace(",", "").strip()
#         try:
#             return float(value)
#         except ValueError:
#             return 0.0
#     return 0.0
#
# def extract_percent(text, pattern):
#     match = re.search(pattern, text, re.IGNORECASE)
#     if match:
#         try:
#             return float(match.group(1).strip())
#         except ValueError:
#             return 0.0
#     return 0.0
#
# def extract_string(text, pattern):
#     match = re.search(pattern, text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     return ""
#
# def extract_data_from_text(text):
#     return {
#         "volume": extract_float(text, r"Traded Volume .*?([\d,.]+)"),
#         "value": extract_float(text, r"Traded Value .*?([\d,.]+)"),
#         "cap": extract_float(text, r"Total Market Cap .*?([\d,.]+)"),
#         "float_cap": extract_float(text, r"Free Float Market Cap .*?([\d,.]+)"),
#         "impact": extract_float(text, r"Impact cost\s*([\d.]+)"),
#         "delivery": extract_percent(text, r"Deliverable / Traded\s+Quantity\s+([\d.]+)\s*%"),
#         "margin": extract_float(text, r"Applicable Margin Rate\s*([\d.]+)"),
#         "daily_vol": extract_float(text, r"Daily Volatility\s*([\d.]+)"),
#         "annual_vol": extract_float(text, r"Annualised Volatility\s*([\d.]+)"),
#         "pe": extract_float(text, r"Adjusted P/E\s*([\d.]+)"),
#         "low52": extract_float(text, r"52 Week Low.*?([\d.]+)"),
#         "high52": extract_float(text, r"52 Week High.*?([\d.]+)"),
#         "index": extract_string(text, r"Index\s+(.*?)\n")
#     }
#
# def populate_fields():
#     try:
#         data = extract_data_from_text(input_box.get("1.0", tk.END))
#         entry_volume.delete(0, tk.END)
#         entry_volume.insert(0, data["volume"])
#         entry_value.delete(0, tk.END)
#         entry_value.insert(0, data["value"])
#         entry_cap.delete(0, tk.END)
#         entry_cap.insert(0, data["cap"])
#         entry_float_cap.delete(0, tk.END)
#         entry_float_cap.insert(0, data["float_cap"])
#         entry_impact.delete(0, tk.END)
#         entry_impact.insert(0, data["impact"])
#         entry_delivery.delete(0, tk.END)
#         entry_delivery.insert(0, data["delivery"])
#         entry_margin.delete(0, tk.END)
#         entry_margin.insert(0, data["margin"])
#         entry_daily_vol.delete(0, tk.END)
#         entry_daily_vol.insert(0, data["daily_vol"])
#         entry_annual_vol.delete(0, tk.END)
#         entry_annual_vol.insert(0, data["annual_vol"])
#         entry_pe.delete(0, tk.END)
#         entry_pe.insert(0, data["pe"])
#         entry_52low.delete(0, tk.END)
#         entry_52low.insert(0, data["low52"])
#         entry_52high.delete(0, tk.END)
#         entry_52high.insert(0, data["high52"])
#         entry_index.delete(0, tk.END)
#         entry_index.insert(0, data["index"])
#     except Exception as e:
#         messagebox.showerror("Parse Error", f"Error parsing data: {str(e)}")
#
# def get_market_cap_segment(market_cap):
#     if market_cap < 5000:
#         return "Small Cap"
#     elif 5000 <= market_cap <= 20000:
#         return "Mid Cap"
#     else:
#         return "Large Cap"
#
# def evaluate_stock():
#     try:
#         volume = float(entry_volume.get())
#         value = float(entry_value.get())
#         cap = float(entry_cap.get())
#         float_cap = float(entry_float_cap.get())
#         impact_cost = float(entry_impact.get())
#         deliverable_pct = float(entry_delivery.get())
#         margin = float(entry_margin.get())
#         daily_vol = float(entry_daily_vol.get())
#         annual_vol = float(entry_annual_vol.get())
#         pe_ratio = float(entry_pe.get())
#         low52 = float(entry_52low.get())
#         high52 = float(entry_52high.get())
#         index = entry_index.get()
#
#         segment = get_market_cap_segment(cap)
#         high_score = 0
#         good_score = 0
#
#         if segment == "Small Cap":
#             vol_th = (5, 20)
#             val_th = (100, 300)
#         elif segment == "Mid Cap":
#             vol_th = (10, 50)
#             val_th = (300, 800)
#         else:
#             vol_th = (20, 100)
#             val_th = (500, 2000)
#
#         if volume > vol_th[1]:
#             high_score += 1
#         elif volume >= vol_th[0]:
#             good_score += 1
#
#         if value > val_th[1]:
#             high_score += 1
#         elif value >= val_th[0]:
#             good_score += 1
#
#         if cap > 20000:
#             high_score += 1
#         elif cap >= 5000:
#             good_score += 1
#
#         if high_score == 3:
#             result = f"🔥 High Recommend ({segment})"
#             color = "green"
#         elif high_score >= 2 or (high_score == 1 and good_score >= 2):
#             result = f"✅ Good ({segment})"
#             color = "orange"
#         else:
#             result = f"❌ Bad ({segment})"
#             color = "red"
#
#         tags = []
#         if cap != 0 and abs(cap - float_cap) / cap < 0.01:
#             tags.append("✅ Public Float Healthy")
#         if impact_cost < 0.1:
#             tags.append("✅ Low Impact Cost")
#         else:
#             tags.append("⚠️ High Impact Cost")
#         if deliverable_pct >= 25:
#             tags.append("✅ Strong Delivery")
#         else:
#             tags.append("⚠️ Low Delivery %")
#         if margin <= 40:
#             tags.append("✅ Margin OK")
#         if 2 <= daily_vol <= 5:
#             tags.append("✅ Volatility OK")
#         elif daily_vol > 6:
#             tags.append("❌ Too Volatile")
#         if 40 <= annual_vol <= 90:
#             tags.append("✅ Swing Range Volatility")
#         if pe_ratio > 80:
#             tags.append("⚠️ High P/E")
#         tags.append(f"Index: {index}")
#         tags.append(f"52W Range: ₹{low52} - ₹{high52}")
#
#         label_result.config(text=f"Recommendation: {result}", fg=color)
#         label_tags.config(text="\n".join(tags), fg="blue")
#
#     except ValueError:
#         messagebox.showerror("Input Error", "Enter valid numeric values.")
#
# # GUI Setup
# root = tk.Tk()
# root.title("Swing Trade Evaluator (Auto-Parse Enabled)")
#
# fields = [
#     ("Traded Volume (Lakhs):", "entry_volume"),
#     ("Traded Value (₹ Cr.):", "entry_value"),
#     ("Market Cap (₹ Cr.):", "entry_cap"),
#     ("Free Float Cap (₹ Cr.):", "entry_float_cap"),
#     ("Impact Cost:", "entry_impact"),
#     ("% Deliverable Quantity:", "entry_delivery"),
#     ("Applicable Margin Rate:", "entry_margin"),
#     ("Daily Volatility (%):", "entry_daily_vol"),
#     ("Annualised Volatility (%):", "entry_annual_vol"),
#     ("P/E Ratio:", "entry_pe"),
#     ("52W Low Price:", "entry_52low"),
#     ("52W High Price:", "entry_52high"),
#     ("Index Name:", "entry_index"),
# ]
#
# entries = {}
# for i, (label_text, var_name) in enumerate(fields):
#     tk.Label(root, text=label_text).grid(row=i, column=0, padx=10, pady=2, sticky="e")
#     entry = tk.Entry(root)
#     entry.grid(row=i, column=1, padx=10, pady=2)
#     entries[var_name] = entry
#
# entry_volume = entries["entry_volume"]
# entry_value = entries["entry_value"]
# entry_cap = entries["entry_cap"]
# entry_float_cap = entries["entry_float_cap"]
# entry_impact = entries["entry_impact"]
# entry_delivery = entries["entry_delivery"]
# entry_margin = entries["entry_margin"]
# entry_daily_vol = entries["entry_daily_vol"]
# entry_annual_vol = entries["entry_annual_vol"]
# entry_pe = entries["entry_pe"]
# entry_52low = entries["entry_52low"]
# entry_52high = entries["entry_52high"]
# entry_index = entries["entry_index"]
#
# # Buttons
# tk.Button(root, text="Evaluate", command=evaluate_stock).grid(row=len(fields), column=0, columnspan=2, pady=5)
# tk.Button(root, text="📥 Auto-Fill From Raw Data", command=populate_fields).grid(row=len(fields)+1, column=0, columnspan=2, pady=5)
#
# # Output Labels
# label_result = tk.Label(root, text="", font=("Arial", 13, "bold"))
# label_result.grid(row=len(fields)+2, column=0, columnspan=2, pady=5)
#
# label_tags = tk.Label(root, text="", font=("Arial", 10), justify="left")
# label_tags.grid(row=len(fields)+3, column=0, columnspan=2, pady=5)
#
# # Input Text Box
# tk.Label(root, text="Paste Raw Data Below:").grid(row=len(fields)+4, column=0, columnspan=2)
# input_box = tk.Text(root, height=12, width=50)
# input_box.grid(row=len(fields)+5, column=0, columnspan=2, padx=10, pady=10)
#
# root.mainloop()




import tkinter as tk
from tkinter import messagebox
import re

# ----------------- Parsing Helpers -----------------

def extract_float(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        value = match.group(1).replace(",", "").strip()
        try:
            return float(value)
        except:
            return 0.0
    return 0.0


def extract_percent(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1).strip())
        except:
            return 0.0
    return 0.0

def extract_string(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

# ----------------- Auto Extract -----------------

def extract_data_from_text(text):
    return {
        "price": extract_float(text, r"Close\s*\*\s*([\d.]+)"),
        "vwap": extract_float(text, r"VWAP\s*([\d.]+)"),
        "upper": extract_float(text, r"Upper Band\s*([\d.]+)"),
        "lower": extract_float(text, r"Lower Band\s*([\d.]+)"),
        "week_return": extract_percent(text, r"1W\s*(-?[\d.]+)%"),

        "volume": extract_float(text, r"Traded Volume.*?([\d,]+\.?\d*)"),
        "value": extract_float(text, r"Traded Value.*?([\d,]+\.?\d*)"),
        "cap": extract_float(text, r"Total Market Cap.*?([\d,]+\.?\d*)"),
        "float_cap": extract_float(text, r"Free Float Market Cap.*?([\d,]+\.?\d*)"),


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
    data = extract_data_from_text(input_box.get("1.0", tk.END))
    for key in entries:
        entries[key].delete(0, tk.END)
        entries[key].insert(0, data.get(key, ""))

# ----------------- Core Logic -----------------

def get_market_cap_segment(market_cap):
    if market_cap < 5000:
        return "Small Cap"
    elif market_cap <= 20000:
        return "Mid Cap"
    else:
        return "Large Cap"

def evaluate_stock():
    try:
        d = {k: float(entries[k].get()) if k not in ["index"] else entries[k].get() for k in entries}

        segment = get_market_cap_segment(d["cap"])
        high_score = 0
        structure_score = 0
        tags = []

        # ---------- Quality Layer ----------
        if d["impact"] < 0.1:
            high_score += 1
            tags.append("✅ Low Impact Cost")

        if d["delivery"] >= 25:
            high_score += 1
            tags.append("✅ Strong Delivery")

        if 2 <= d["daily_vol"] <= 5:
            high_score += 1
            tags.append("✅ Daily Volatility OK")

        if 40 <= d["annual_vol"] <= 90:
            high_score += 1
            tags.append("✅ Annual Volatility in Swing Range")

        if abs(d["cap"] - d["float_cap"]) / d["cap"] < 0.02:
            high_score += 1
            tags.append("✅ Healthy Free Float")

        # ---------- Structure Layer ----------
        # VWAP
        if abs(d["price"] - d["vwap"]) / d["vwap"] < 0.01:
            structure_score += 1
            tags.append("✅ At VWAP Zone")

        # 52W Pullback
        dist_high = (d["high52"] - d["price"]) / d["high52"] * 100
        if 10 <= dist_high <= 30:
            structure_score += 1
            tags.append("✅ Healthy Pullback From High")

        # Circuit Safety
        if d["price"] > d["lower"] * 1.1:
            structure_score += 1
            tags.append("✅ Away From Lower Circuit")

        # Crash Detection
        if d["week_return"] < -12:
            tags.append("⚠️ Sharp Recent Fall (Wait for base)")

        # ---------- Final Decision ----------
        final_score = high_score + structure_score

        if final_score >= 7:
            result = "🔥 A+ SWING SETUP"
            color = "green"
        elif final_score >= 5:
            result = "✅ A SWING SETUP"
            color = "orange"
        elif final_score >= 3:
            result = "⚠️ B SETUP"
            color = "brown"
        else:
            result = "❌ AVOID"
            color = "red"

        tags.append(f"Market Cap: {segment}")
        tags.append(f"52W Range: ₹{d['low52']} - ₹{d['high52']}")
        tags.append(f"Index: {d['index']}")

        label_result.config(text=result, fg=color)
        label_tags.config(text="\n".join(tags))

    except:
        messagebox.showerror("Error", "Invalid numeric values")

# # ----------------- GUI -----------------
#
# root = tk.Tk()
# root.title("Professional Swing Trade Evaluator")
#
# fields = [
#     ("Current Price", "price"),
#     ("VWAP", "vwap"),
#     ("Upper Band", "upper"),
#     ("Lower Band", "lower"),
#     ("1W Return %", "week_return"),
#
#     ("Traded Volume (Lakhs)", "volume"),
#     ("Traded Value (₹ Cr)", "value"),
#     ("Market Cap (₹ Cr)", "cap"),
#     ("Free Float Cap (₹ Cr)", "float_cap"),
#     ("Impact Cost", "impact"),
#     ("Delivery %", "delivery"),
#     ("Margin", "margin"),
#     ("Daily Volatility", "daily_vol"),
#     ("Annual Volatility", "annual_vol"),
#     ("P/E Ratio", "pe"),
#     ("52W Low", "low52"),
#     ("52W High", "high52"),
#     ("Index", "index")
# ]
#
# entries = {}
# for i, (label, key) in enumerate(fields):
#     tk.Label(root, text=label).grid(row=i, column=0, sticky="e")
#     e = tk.Entry(root)
#     e.grid(row=i, column=1)
#     entries[key] = e
#
# tk.Button(root, text="📥 Auto-Fill From Raw Data", command=populate_fields).grid(row=len(fields), column=0, columnspan=2)
# tk.Button(root, text="Evaluate", command=evaluate_stock).grid(row=len(fields)+1, column=0, columnspan=2)
#
# label_result = tk.Label(root, text="", font=("Arial", 14, "bold"))
# label_result.grid(row=len(fields)+2, column=0, columnspan=2)
#
# label_tags = tk.Label(root, text="", justify="left")
# label_tags.grid(row=len(fields)+3, column=0, columnspan=2)
#
# tk.Label(root, text="Paste NSE Raw Data:").grid(row=len(fields)+4, column=0, columnspan=2)
# input_box = tk.Text(root, height=10, width=60)
# input_box.grid(row=len(fields)+5, column=0, columnspan=2)
#
# root.mainloop()

# gui  2


# ----------------- GUI -----------------

root = tk.Tk()
root.title("Professional Swing Trade Evaluator")

# Set good default size for 1366x768 screens
root.geometry("1200x700")
root.minsize(1000, 600)

# Make root expandable
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# -------- Left Panel (Inputs + Results) --------
left_frame = tk.Frame(root, padx=10, pady=10)
left_frame.grid(row=0, column=0, sticky="nsew")

# -------- Right Panel (Raw Data Paste Box) --------
right_frame = tk.Frame(root, padx=10, pady=10)
right_frame.grid(row=0, column=1, sticky="nsew")

root.grid_columnconfigure(0, weight=3)
root.grid_columnconfigure(1, weight=2)

# Fields (we will show them in 3 columns)
fields = [
    ("Current Price", "price"),
    ("VWAP", "vwap"),
    ("Upper Band", "upper"),
    ("Lower Band", "lower"),
    ("1W Return %", "week_return"),

    ("Traded Volume (Lakhs)", "volume"),
    ("Traded Value (₹ Cr)", "value"),
    ("Market Cap (₹ Cr)", "cap"),
    ("Free Float Cap (₹ Cr)", "float_cap"),
    ("Impact Cost", "impact"),

    ("Delivery %", "delivery"),
    ("Margin", "margin"),
    ("Daily Volatility", "daily_vol"),
    ("Annual Volatility", "annual_vol"),
    ("P/E Ratio", "pe"),

    ("52W Low", "low52"),
    ("52W High", "high52"),
    ("Index", "index"),
]

entries = {}

# 3 columns layout
cols = 3
for i, (label, key) in enumerate(fields):
    r = i // cols
    c = (i % cols) * 2

    tk.Label(left_frame, text=label, font=("Segoe UI", 10, "bold"))\
        .grid(row=r, column=c, sticky="e", padx=5, pady=5)

    e = tk.Entry(left_frame, font=("Segoe UI", 10), width=18)
    e.grid(row=r, column=c+1, sticky="w", padx=5, pady=5)
    entries[key] = e

# Make columns stretch nicely
for i in range(cols * 2):
    left_frame.grid_columnconfigure(i, weight=1)

# -------- Buttons --------
btn_frame = tk.Frame(left_frame, pady=10)
btn_frame.grid(row=(len(fields)//cols)+1, column=0, columnspan=cols*2, sticky="ew")

tk.Button(btn_frame, text="📥 Auto-Fill From Raw Data",
          font=("Segoe UI", 11, "bold"),
          bg="#4CAF50", fg="white",
          command=populate_fields).pack(side="left", expand=True, fill="x", padx=5)

tk.Button(btn_frame, text="Evaluate",
          font=("Segoe UI", 11, "bold"),
          bg="#2196F3", fg="white",
          command=evaluate_stock).pack(side="left", expand=True, fill="x", padx=5)

# -------- Result Area --------
label_result = tk.Label(left_frame, text="",
                        font=("Segoe UI", 16, "bold"))
label_result.grid(row=(len(fields)//cols)+2,
                  column=0, columnspan=cols*2, pady=10)

label_tags = tk.Label(left_frame, text="",
                      font=("Segoe UI", 10),
                      justify="left", anchor="w")
label_tags.grid(row=(len(fields)//cols)+3,
                column=0, columnspan=cols*2, sticky="w")

# -------- Right Panel: Raw NSE Data --------
tk.Label(right_frame, text="Paste NSE Raw Data:",
         font=("Segoe UI", 12, "bold")).pack(anchor="w")

input_box = tk.Text(right_frame,
                    font=("Consolas", 10),
                    wrap="word")
input_box.pack(expand=True, fill="both", pady=5)

root.mainloop()
