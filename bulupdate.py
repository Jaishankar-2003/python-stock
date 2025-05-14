import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

# ⚙️ Step 1: Load symbols and filter only EQ
symbols_df = pd.read_csv("nse_symbols.csv")
symbol_col = next((c for c in symbols_df.columns if 'symbol' in c.lower()), 'SYMBOL')
series_col = next((c for c in symbols_df.columns if 'series' in c.lower()), 'SERIES')

symbols_df = symbols_df[symbols_df[series_col].str.strip().eq('EQ')]
symbols = [s.strip() + ".NS" for s in symbols_df[symbol_col]]

# 🔁 Step 2: Download Data in Batches
def download_batch(batch):
    for attempt in range(3):
        try:
            return yf.download(
                tickers=" ".join(batch),
                period="3mo",
                interval="1d",
                group_by="ticker",
                threads=True,
                progress=False,
                timeout=60  # Increased timeout to 60 seconds
            )
        except Exception as e:
            print(f"Retry {attempt + 1}/3 for batch failed: {e}")
            time.sleep(5)
    return None

# 🎯 Step 3: Swing Strategy
selected = []
chunk_size = 50
chunks = [symbols[i:i + chunk_size] for i in range(0, len(symbols), chunk_size)]

# Keep track of failures for analysis
failed_symbols = []

for chunk in chunks:
    data = download_batch(chunk)
    if data is None:
        print(f"⚠️ Failed to download data for batch {chunk}. Skipping...")
        continue

    for sym in chunk:
        try:
            df = data.get(sym)
            if df is None or df.empty or len(df) < 50:
                failed_symbols.append(sym)
                continue

            # Clean up data
            df = df.copy()
            df.dropna(subset=['Close', 'Open', 'High', 'Low', 'Volume'], inplace=True)

            # Indicators
            df["EMA_20"] = ta.ema(df["Close"], length=20)
            df["EMA_50"] = ta.ema(df["Close"], length=50)
            df["RSI"] = ta.rsi(df["Close"], length=14)

            macd = ta.macd(df["Close"], fast=12, slow=26, signal=9)
            df["MACD_Line"] = macd["MACD_12_26_9"]
            df["MACD_Signal"] = macd["MACDs_12_26_9"]
            df["Vol_SMA_20"] = df["Volume"].rolling(window=20).mean()
            df["15d_return"] = df["Close"].pct_change(15, fill_method=None) * 100
            df["Recent_High"] = df["High"].rolling(window=15).max()

            # Drop rows with missing indicators or critical data
            df.dropna(subset=["EMA_20", "EMA_50", "RSI", "MACD_Line", "MACD_Signal", "Vol_SMA_20", "15d_return", "Recent_High"], inplace=True)

            if df.empty or len(df) < 2:
                failed_symbols.append(sym)
                continue

            latest = df.iloc[-1]
            prev = df.iloc[-2]

            required_cols = ["EMA_20", "EMA_50", "RSI", "MACD_Line", "MACD_Signal", "Vol_SMA_20", "15d_return", "Recent_High"]
            if pd.isna(latest[required_cols]).any():
                failed_symbols.append(sym)
                continue

            # 📌 Apply All Swing Conditions
            if (
                latest["Close"] > latest["EMA_20"] > latest["EMA_50"]
                and 50 < latest["RSI"] < 70
                and latest["MACD_Line"] > latest["MACD_Signal"]
                and latest["Volume"] > latest["Vol_SMA_20"]
                and latest["Close"] > latest["Open"]
                and latest["Close"] > prev["Close"]
                and latest["Close"] > 50
                and latest["15d_return"] >= 10
                and latest["Close"] >= latest["Recent_High"]
                and not (latest["RSI"] > 68 and (latest["MACD_Line"] - latest["MACD_Signal"]) < 0.5)
            ):
                selected.append(sym.replace(".NS", ""))

        except Exception as e:
            failed_symbols.append(sym)
            print(f"⚠️ Error processing {sym}: {e}")

# ✅ Step 4: Output
print("\n🎯 Swing Trade Candidates:")
for stock in selected:
    print(f"  • {stock}")
print(f"\nTotal matches: {len(selected)}")

# Print failed stocks for analysis
if failed_symbols:
    print("\nFailed Symbols (with errors):")
    for failed in failed_symbols:
        print(f"  • {failed}")
