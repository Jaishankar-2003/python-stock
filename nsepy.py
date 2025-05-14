import pandas as pd
import numpy as np
import time
import yfinance as yf
import pandas_ta as ta

# ⚙️ Step 1: Load NSE Symbols
symbols_df = pd.read_csv("data.csv")
symbols = [s.strip() + ".NS" for s in symbols_df['SYMBOL']]


# 🔁 Step 2: Download Historical Data with Enhanced Error Handling
def download_batch(batch):
    data = {}
    for sym in batch:
        for attempt in range(3):
            try:
                print(f"Fetching data for {sym} (Attempt {attempt + 1})...")
                df = yf.download(sym, period="3mo", interval="1d", progress=False)
                if df is not None and not df.empty:
                    data[sym] = df
                    break  # Break the retry loop if successful
                else:
                    print(f"No data received for {sym} on attempt {attempt + 1}")
                    time.sleep(5)  # Add a delay before retrying
            except Exception as e:
                print(f"Error fetching {sym} on attempt {attempt + 1}: {e}")
                time.sleep(5)  # Add a delay before retrying
        if sym not in data:
            print(f"Failed to download data for {sym} after 3 attempts. Skipping.")
    return data


# 🎯 Step 3: Scan for Swing Setups
selected = []
chunk_size = 50
chunks = [symbols[i:i + chunk_size] for i in range(0, len(symbols), chunk_size)]

for chunk in chunks:
    data = download_batch(chunk)
    if not data:
        print("No data downloaded for this chunk. Continuing...")
        continue

    for sym in chunk:
        if sym not in data:  # Check if the symbol was successfully downloaded
            continue
        try:
            df = data.get(sym)

            if df is None or df.empty or len(df) < 50:
                print(f"Skipping {sym}: Insufficient data")
                continue

            print(f"\n--- Debugging {sym} ---")
            print(f"Type of df: {type(df)}")
            if df is not None:
                print(f"Shape of df: {df.shape}")
                print(f"First few rows of df:\n{df.head()}")

            # --- Handle MultiIndex ---
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)  # Use the top level
                print("MultiIndex flattened.")  # Added this line
            elif not {'Close', 'Open', 'High', 'Low', 'Volume'}.issubset(df.columns):
                print(f"Skipping {sym}:  Missing essential columns")
                continue

            df = df.copy()
            df.dropna(inplace=True)

            # Add indicators
            try:
                df["EMA_20"] = ta.ema(df["Close"], length=20)
                df["EMA_50"] = ta.ema(df["Close"], length=50)
                df["RSI"] = ta.rsi(df["Close"], length=14)
                macd = ta.macd(df["Close"], fast=12, slow=26, signal=9)
                df["MACD_Line"] = macd["MACD_12_26_9"]
                df["MACD_Signal"] = macd["MACDs_12_26_9"]
                df["Vol_SMA_20"] = df["Volume"].rolling(window=20).mean()
                df["15d_return"] = df["Close"].pct_change(15) * 100
                df["Recent_High_15d"] = df["High"].rolling(window=15).max()
            except Exception as e:
                print(f"Error calculating indicators for {sym}: {e}")
                continue  # Skip to the next symbol if indicator calculation fails

            # Latest data
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            required_cols = [
                "EMA_20", "EMA_50", "RSI", "MACD_Line",
                "MACD_Signal", "Vol_SMA_20", "15d_return", "Recent_High_15d"
            ]
            if pd.isna(latest[required_cols]).any():
                print(f"Skipping {sym}: Missing indicator data")
                continue

            # --- Print statements for debugging ---
            print(f"\n--- Checking conditions for {sym} ---")
            print(f"Close: {latest['Close']}, EMA_20: {latest['EMA_20']}, EMA_50: {latest['EMA_50']}")
            print(f"RSI: {latest['RSI']}")
            print(f"MACD_Line: {latest['MACD_Line']}, MACD_Signal: {latest['MACD_Signal']}")
            print(f"Volume: {latest['Volume']}, Vol_SMA_20: {latest['Vol_SMA_20']}")
            print(f"Open: {latest['Open']}, Previous Close: {prev['Close']}")
            print(f"15d_return: {latest['15d_return']}")
            print(f"Recent_High_15d: {latest['Recent_High_15d']}")

            # 🚨 Filter conditions
            if (
                    latest["Close"] > latest["EMA_20"] > latest["EMA_50"]
                    and 50 < latest["RSI"] < 70
                    and latest["MACD_Line"] > latest["MACD_Signal"]
                    and latest["Volume"] > latest["Vol_SMA_20"]
                    and latest["Close"] > latest["Open"]
                    and latest["Close"] > prev["Close"]
                    and latest["Close"] > 50
                    and latest["15d_return"] >= 10
                    and latest["Close"] >= latest["Recent_High_15d"]
                    and not (latest["RSI"] > 68 and (latest["MACD_Line"] - latest["MACD_Signal"]) < 0.5)
            ):
                selected.append(sym)
                print(f"{sym} passed the filters")

        except Exception as e:
            print(f"⚠️ Error processing {sym}: {e}")

# ✅ Step 4: Output Result
print("\n🎯 Swing Trade Candidates:")
if selected:
    for stock in selected:
        print(f"  • {stock}")
    print(f"\nTotal matches: {len(selected)}")
else:
    print("No stocks passed the filters")

