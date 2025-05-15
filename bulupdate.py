import pandas as pd
import pandas_ta as ta
import yfinance as yf
from datetime import datetime, timedelta
import time

# Step 1: Load symbols and add .NS suffix
symbols_df = pd.read_csv("filtered_stock_names.csv")
symbols = [s.strip() + ".NS" for s in symbols_df['SYMBOL']]

# Step 2: Initialize
selected = []
yesterday = (datetime.now() - timedelta(days=1)).date()

# Step 3: Process each symbol
for symbol in symbols:
    try:
        print(f"\n🔍 Fetching data for: {symbol}")
        df = yf.download(symbol, period="3mo", interval="1d", progress=False, auto_adjust=False)

        if df is None or df.empty or len(df) < 50:
            print(f"❌ Skipping {symbol}: Not enough data")
            continue

        df.index = pd.to_datetime(df.index)
        df = df[~df.index.duplicated(keep='last')]

        if df.index[-1].date() < yesterday:
            print(f"⚠️ Skipping {symbol}: Data outdated ({df.index[-1].date()})")
            continue

        # Indicators
        df["EMA_20"] = ta.ema(df["Close"], length=20)
        df["EMA_50"] = ta.ema(df["Close"], length=50)
        df["RSI"] = ta.rsi(df["Close"], length=14)
        df["Vol_SMA_20"] = df["Volume"].rolling(window=20).mean()
        df["15d_return"] = df["Close"].pct_change(15) * 100
        df["Recent_High_15d"] = df["High"].rolling(window=15).max()

        macd = ta.macd(df["Close"])
        if macd is not None and not macd.empty:
            df["MACD_Line"] = macd["MACD_12_26_9"]
            df["MACD_Signal"] = macd["MACDs_12_26_9"]
        else:
            print(f"⚠️ MACD missing for {symbol}. Skipping MACD condition.")
            df["MACD_Line"] = None
            df["MACD_Signal"] = None

        df.dropna(inplace=True)

        if len(df) < 2:
            print(f"❌ Skipping {symbol}: Insufficient data after indicators")
            continue

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # Conditions
        conditions = [
            latest["Close"] > latest["EMA_20"] > latest["EMA_50"],
            50 < latest["RSI"] < 70,
            latest["Volume"] > latest["Vol_SMA_20"],
            latest["Close"] > latest["Open"],
            latest["Close"] > prev["Close"],
            latest["Close"] > 50,
            latest["15d_return"] >= 10,
            latest["Close"] >= latest["Recent_High_15d"]
        ]

        # Optional MACD condition
        if pd.notna(latest["MACD_Line"]) and pd.notna(latest["MACD_Signal"]):
            conditions.append(latest["MACD_Line"] > latest["MACD_Signal"])
            if latest["RSI"] > 68 and (latest["MACD_Line"] - latest["MACD_Signal"]) < 0.5:
                print(f"❌ Rejected: {symbol} (MACD-RSI fakeout)")
                continue

        if all(conditions):
            print(f"✅ Selected: {symbol}")
            selected.append(symbol)
        else:
            print(f"❌ Rejected: {symbol} (Did not meet all conditions)")

    except Exception as e:
        print(f"⚠️ Error processing {symbol}: {e}")
    time.sleep(1.5)  # Slow down requests

# Step 4: Final Output
print("\n🎯 Final Swing Trade Candidates:")
if selected:
    for sym in selected:
        print(f"  • {sym}")
    print(f"\n✅ Total Matches: {len(selected)}")
else:
    print("❌ No stocks matched the swing criteria.")
