import pandas as pd

def clean_num(x):
    s = str(x).replace(",", "").strip()
    if s in ("", "-", "NA", "nan"):
        return None
    try:
        return float(s)
    except:
        return None

def run_screener(file):
    df = pd.read_csv(file)

    # rename columns to simple names (adjust if your CSV headers differ slightly)
    df = df.rename(columns={
        "SYMBOL \n": "symbol",
        "LTP \n": "price",
        "VALUE \n (₹ Crores)": "value_cr",
        "%CHNG \n": "day_change",
        "52W H \n": "high52",
        "52W L \n": "low52"
    })

    # clean numeric columns safely
    for col in ["price", "value_cr", "day_change", "high52", "low52"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_num)

    # drop rows where essential data is missing
    df = df.dropna(subset=["price", "value_cr", "day_change", "high52"])

    results = []

    for _, r in df.iterrows():
        price = r["price"]
        value = r["value_cr"]
        change = r["day_change"]
        high52 = r["high52"]

        # liquidity filter
        if value < 200:
            continue

        # positive day momentum
        if change <= 0:
            continue

        # pullback from 52W high
        pullback = (high52 - price) / high52 * 100
        if pullback < 10 or pullback > 40:
            continue

        results.append({
            "symbol": r["symbol"],
            "price": price,
            "value": value,
            "change": change,
            "pullback": pullback
        })

    if not results:
        print("No swing candidates found.")
        return

    # sort by traded value descending (top liquidity first)
    results = sorted(results, key=lambda x: x["value"], reverse=True)

    # keep only top 15 candidates
    results = results[:15]

    print("\nSwing Candidates (Top 15 by Liquidity):\n")
    print(f"{'Symbol':12} {'Price':>10} {'ValueCr':>10} {'Day%':>8} {'Pullback%':>12}")

    for r in results:
        print(f"{r['symbol']:12} "
              f"{r['price']:10.2f} "
              f"{r['value']:10.2f} "
              f"{r['change']:8.2f} "
              f"{r['pullback']:12.2f}")

# run on your big NSE file
run_screener("csv file/FMCG-31-Jan-2026.csv")
