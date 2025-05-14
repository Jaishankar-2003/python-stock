import yfinance as yf
import pandas as pd
import ta

# List of NSE stock symbols (you can expand this list)
nse_stocks = ["RELIANCE.NS", "INFY.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS"]

# Store stocks that meet criteria
selected_stocks = []

for symbol in nse_stocks:
    try:
        df = yf.download(symbol, period="3mo", interval="1d")
        df.dropna(inplace=True)

        # Indicators
        df["EMA_20"] = ta.trend.ema_indicator(df["Close"], window=20)
        df["EMA_50"] = ta.trend.ema_indicator(df["Close"], window=50)
        df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
        macd = ta.trend.macd(df["Close"])
        df["MACD_Line"] = macd.macd()
        df["MACD_Signal"] = macd.macd_signal()
        df["Volume_SMA_20"] = df["Volume"].rolling(window=20).mean()

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # Conditions
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
            selected_stocks.append(symbol)
    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# Output results
print("✅ Stocks matching swing trade criteria:")
for stock in selected_stocks:
    print(stock)
