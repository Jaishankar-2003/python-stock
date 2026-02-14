# import pandas as pd
#
# def clean_num(x):
#     s = str(x).replace(",", "").strip()
#     if s in ("", "-", "NA", "nan"):
#         return None
#     try:
#         return float(s)
#     except:
#         return None
#
# def run_screener(file):
#     df = pd.read_csv(file)
#
#     # rename columns to simple names (adjust if your CSV headers differ slightly)
#     df = df.rename(columns={
#         "SYMBOL \n": "symbol",
#         "LTP \n": "price",
#         "VALUE \n (₹ Crores)": "value_cr",
#         "%CHNG \n": "day_change",
#         "52W H \n": "high52",
#         "52W L \n": "low52"
#     })
#
#     # clean numeric columns safely
#     for col in ["price", "value_cr", "day_change", "high52", "low52"]:
#         if col in df.columns:
#             df[col] = df[col].apply(clean_num)
#
#     # drop rows where essential data is missing
#     df = df.dropna(subset=["price", "value_cr", "day_change", "high52"])
#
#     results = []
#
#     for _, r in df.iterrows():
#         price = r["price"]
#         value = r["value_cr"]
#         change = r["day_change"]
#         high52 = r["high52"]
#
#         # liquidity filter
#         if value < 200:
#             continue
#
#         # positive day momentum
#         if change <= 0:
#             continue
#
#         # pullback from 52W high
#         pullback = (high52 - price) / high52 * 100
#         if pullback < 10 or pullback > 40:
#             continue
#
#         results.append({
#             "symbol": r["symbol"],
#             "price": price,
#             "value": value,
#             "change": change,
#             "pullback": pullback
#         })
#
#     if not results:
#         print("No swing candidates found.")
#         return
#
#     # sort by traded value descending (top liquidity first)
#     results = sorted(results, key=lambda x: x["value"], reverse=True)
#
#     # keep only top 15 candidates
#     results = results[:20]
#
#     print("\nSwing Candidates (Top 15 by Liquidity):\n")
#     print(f"{'Symbol':12} {'Price':>10} {'ValueCr':>10} {'Day%':>8} {'Pullback%':>12}")
#
#     for r in results:
#         print(f"{r['symbol']:12} "
#               f"{r['price']:10.2f} "
#               f"{r['value']:10.2f} "
#               f"{r['change']:8.2f} "
#               f"{r['pullback']:12.2f}")
#
# # run on your big NSE file
# run_screener("csv file/MW-NIFTY-MIDSMALLCAP-400-08-Feb-2026.csv")



# import pandas as pd
# import glob
# import os
#
# def clean_num(x):
#     s = str(x).replace(",", "").strip()
#     if s in ("", "-", "NA", "nan", "None"):
#         return None
#     try:
#         return float(s)
#     except:
#         return None
#
#
# def run_screener_on_df(df, source_file=""):
#     # rename columns to simple names (adjust if your CSV headers differ slightly)
#     df = df.rename(columns={
#         "SYMBOL \n": "symbol",
#         "LTP \n": "price",
#         "VALUE \n (₹ Crores)": "value_cr",
#         "%CHNG \n": "day_change",
#         "52W H \n": "high52",
#         "52W L \n": "low52"
#     })
#
#     # clean numeric columns safely
#     for col in ["price", "value_cr", "day_change", "high52", "low52"]:
#         if col in df.columns:
#             df[col] = df[col].apply(clean_num)
#
#     # drop rows where essential data is missing
#     df = df.dropna(subset=["symbol", "price", "value_cr", "day_change", "high52"])
#
#     results = []
#
#     for _, r in df.iterrows():
#         price = r["price"]
#         value = r["value_cr"]
#         change = r["day_change"]
#         high52 = r["high52"]
#
#         # liquidity filter
#         if value < 200:
#             continue
#
#         # positive day momentum
#         if change <= 1.0:
#             continue
#
#         # pullback from 52W high
#         pullback = (high52 - price) / high52 * 100
#         if pullback < 10 or pullback > 40:
#             continue
#
#         results.append({
#             "source_file": os.path.basename(source_file),
#             "symbol": r["symbol"],
#             "price": price,
#             "value": value,
#             "change": change,
#             "pullback": pullback
#         })
#
#     return results
#
#
# def run_screener_multiple_files(folder_pattern="csv file/*.csv", top_n=20):
#     csv_files = glob.glob(folder_pattern)
#
#     if not csv_files:
#         print("❌ No CSV files found.")
#         return
#
#     all_results = []
#
#     for file in csv_files:
#         try:
#             df = pd.read_csv(file)
#             res = run_screener_on_df(df, source_file=file)
#
#             if res:
#                 print(f"✅ {os.path.basename(file)} → {len(res)} candidates")
#             else:
#                 print(f"⚠️ {os.path.basename(file)} → No candidates")
#
#             all_results.extend(res)
#
#         except Exception as e:
#             print(f"❌ Error in {file}: {e}")
#
#     if not all_results:
#         print("\nNo swing candidates found in any file.")
#         return
#
#     # sort by traded value descending (top liquidity first)
#     all_results = sorted(all_results, key=lambda x: x["value"], reverse=True)
#
#     # keep only top N candidates
#     all_results = all_results[:top_n]
#
#     print(f"\n📌 FINAL SWING CANDIDATES (Top {top_n} by Liquidity)\n")
#     print(f"{'SourceFile':25} {'Symbol':12} {'Price':>10} {'ValueCr':>10} {'Day%':>8} {'Pullback%':>12}")
#
#     for r in all_results:
#         print(f"{r['source_file'][:25]:25} "
#               f"{r['symbol'][:12]:12} "
#               f"{r['price']:10.2f} "
#               f"{r['value']:10.2f} "
#               f"{r['change']:8.2f} "
#               f"{r['pullback']:12.2f}")
#
#
# # =========================================================
# # RUN
# # =========================================================
#
# run_screener_multiple_files("csv file/*.csv", top_n=500)
#

#=================================================================================================

import pandas as pd
import glob
import os

def clean_num(x):
    s = str(x).replace(",", "").strip()
    if s in ("", "-", "NA", "nan", "None"):
        return None
    try:
        return float(s)
    except:
        return None


def run_screener_on_df(df, source_file=""):
    df = df.rename(columns={
        "SYMBOL \n": "symbol",
        "LTP \n": "price",
        "VALUE \n (₹ Crores)": "value_cr",
        "%CHNG \n": "day_change",
        "52W H \n": "high52",
        "52W L \n": "low52"
    })

    for col in ["price", "value_cr", "day_change", "high52", "low52"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_num)

    df = df.dropna(subset=["symbol", "price", "value_cr", "day_change", "high52", "low52"])

    results = []

    for _, r in df.iterrows():
        symbol = str(r["symbol"]).strip()
        price = r["price"]
        value = r["value_cr"]
        change = r["day_change"]
        high52 = r["high52"]
        low52 = r["low52"]

        # 🟦 1) Liquidity filter
        if value < 300:
            continue

        # 🟦 2) Price filter (avoid penny / junk)
        if price < 50:
            continue

        # 🟦 3) Momentum filter (avoid weak green days)
        if change < 1.0:
            continue

        # 🟦 4) Pullback from 52W High
        pullback = (high52 - price) / high52 * 100
        if pullback < 5 or pullback > 35:
            continue

        # 🟦 5) Range position filter (avoid broken stocks)
        # (how strong stock is inside yearly range)
        if (high52 - low52) <= 0:
            continue

        range_pos = (price - low52) / (high52 - low52) * 100

        # keep only strong zone stocks
        if range_pos < 40:
            continue

        results.append({
            "source_file": os.path.basename(source_file),
            "symbol": symbol,
            "price": price,
            "value": value,
            "change": change,
            "pullback": pullback,
            "range_pos": range_pos
        })

    return results


def run_screener_multiple_files(folder_pattern="csv file/*.csv", top_n=50):
    csv_files = glob.glob(folder_pattern)

    if not csv_files:
        print("❌ No CSV files found.")
        return

    all_results = []

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            res = run_screener_on_df(df, source_file=file)

            if res:
                print(f"✅ {os.path.basename(file)} → {len(res)} candidates")
            else:
                print(f"⚠️ {os.path.basename(file)} → No candidates")

            all_results.extend(res)

        except Exception as e:
            print(f"❌ Error in {file}: {e}")

    if not all_results:
        print("\nNo swing candidates found in any file.")
        return

    # sort by liquidity
    all_results = sorted(all_results, key=lambda x: x["value"], reverse=True)

    all_results = all_results[:top_n]

    print(f"\n📌 FINAL SWING CANDIDATES (Top {top_n})\n")
    print(f"{'SourceFile':25} {'Symbol':12} {'Price':>10} {'ValueCr':>10} {'Day%':>8} {'Pullback%':>12} {'Range%':>10}")

    for r in all_results:
        print(f"{r['source_file'][:25]:25} "
              f"{r['symbol'][:12]:12} "
              f"{r['price']:10.2f} "
              f"{r['value']:10.2f} "
              f"{r['change']:8.2f} "
              f"{r['pullback']:12.2f} "
              f"{r['range_pos']:10.2f}")


run_screener_multiple_files("csv file/*.csv", top_n=500)
