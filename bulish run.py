import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

# Load full list of NSE stock symbols from CSV (downloaded from NSE website)
symbols_df = pd.read_csv("nse_symbols.csv")
symbols = symbols_df['Symbol'].tolist()
symbols = [sym + ".NS" for sym in symbols]  # Add .NS for yfinance compatibility

selected_stocks = []

for symbol in symbols:
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < 50:
            continue
        df.dropna(inplace=True)

        # Technical indicators
        df["EMA_20"] = ta.trend.ema_indicator(df["Close"], window=20)
        df["EMA_50"] = ta.trend.ema_indicator(df["Close"], window=50)
        df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
        macd = ta.trend.macd(df["Close"])
        df["MACD_Line"] = macd.macd()
        df["MACD_Signal"] = macd.macd_signal()
        df["Volume_SMA_20"] = df["Volume"].rolling(window=20).mean()

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        if (
            latest["Close"] > latest["EMA_20"] and
            latest["Close"] > latest["EMA_50"] and
            latest["EMA_20"] > latest["EMA_50"] and
            latest["RSI"] > 50 and
            latest["RSI"] < 70 and
            latest["MACD_Line"] > latest["MACD_Signal"] and
            latest["Volume"] > latest["Volume_SMA_20"] and
            latest["Close"] > latest["Open"] and
            latest["Close"] > previous["Close"] and
            latest["Close"] > 50
        ):
            selected_stocks.append(symbol.replace(".NS", ""))
            print(f"✅ Match: {symbol}")
        else:
            print(f"❌ Not match: {symbol}")

        time.sleep(1)  # To avoid rate-limiting from Yahoo
    except Exception as e:
        print(f"⚠️ Error processing {symbol}: {e}")

# Final results
print("\n🎯 Stocks matching swing trade criteria:")
for stock in selected_stocks:
    print(stock)
