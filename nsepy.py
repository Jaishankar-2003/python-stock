import pandas as pd
import numpy as np
import time
import nsepython
import pandas_ta as ta

# ⚙️ Step 1: Load NSE Symbols and Filter Equity (EQ) Stocks
symbols_df = pd.read_csv("nse_symbols.csv")
symbol_col = next((c for c in symbols_df.columns if 'symbol' in c.lower()), 'SYMBOL')
series_col = next((c for c in symbols_df.columns if 'series' in c.lower()), 'SERIES')
symbols_df = symbols_df[symbols_df[series_col].str.strip().eq('EQ')]
symbols = [s.strip() for s in symbols_df[symbol_col]]

# 🔁 Step 2: Download Historical Data in Batches using `nsepython`
def download_batch(batch):
    for attempt in range(3):
        try:
            data = {}
            for sym in batch:
                data[sym] = nsepython.get_history(symbol=sym, index=False, period='3mo')
            return data
        except Exception as e:
            print(f"Retry {attempt + 1}/3 for batch failed: {e}")
            time.sleep(2)
    return None

# 🎯 Step 3: Scan for Swing Setups
selected = []
chunk_size = 50
chunks = [symbols[i:i + chunk_size] for i in range(0, len(symbols), chunk_size)]

for chunk in chunks:
    data = download_batch(chunk)
    if data is None:
        continue

    for sym in chunk:
        try:
            df = data.get(sym)
            if df is None or df.empty or len(df) < 50:
                continue

            df = df.copy()

            # Add indicators
            df["EMA_20"] = ta.ema(df["Close"], length=20)
            df["EMA_50"] = ta.ema(df["Close"], length=50)
            df["RSI"] = ta.rsi(df["Close"], length=14)
            macd = ta.macd(df["Close"], fast=12, slow=26, signal=9)
            df["MACD_Line"] = macd["MACD_12_26_9"]
            df["MACD_Signal"] = macd["MACDs_12_26_9"]
            df["Vol_SMA_20"] = df["Volume"].rolling(window=20).mean()
            df["15d_return"] = df["Close"].pct_change(15) * 100
            df["Recent_High_15d"] = df["High"].rolling(window=15).max()

            # Latest data
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            required_cols = [
                "EMA_20", "EMA_50", "RSI", "MACD_Line",
                "MACD_Signal", "Vol_SMA_20", "15d_return", "Recent_High_15d"
            ]
            if pd.isna(latest[required_cols]).any():
                continue

            # 🚨 Filter conditions (1, 2, and 4 only)
            if (
                latest["Close"] > latest["EMA_20"] > latest["EMA_50"]
                and 50 < latest["RSI"] < 70
                and latest["MACD_Line"] > latest["MACD_Signal"]
                and latest["Volume"] > latest["Vol_SMA_20"]
                and latest["Close"] > latest["Open"]
                and latest["Close"] > prev["Close"]
                and latest["Close"] > 50
                and latest["15d_return"] >= 10                                  # ✅ 10% up move
                and latest["Close"] >= latest["Recent_High_15d"]                # ✅ breakout
                and not (latest["RSI"] > 68 and (latest["MACD_Line"] - latest["MACD_Signal"]) < 0.5)  # ✅ avoid weak MACD gap
            ):
                selected.append(sym)

        except Exception as e:
            print(f"⚠️ Error processing {sym}: {e}")

# ✅ Step 4: Output Result
print("\n🎯 Swing Trade Candidates:")
for stock in selected:
    print(f"  • {stock}")
print(f"\nTotal matches: {len(selected)}")
