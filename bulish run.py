import yfinance as yf
import pandas as pd
import pandas_ta  # no need to import ta.trend or ta.momentum
import numpy as _np
_np.NaN = _np.nan  # monkey-patch for NaN if needed

# 1) CSV symbols load
symbols_df = pd.read_csv("nse_symbols.csv")
symbol_col = [c for c in symbols_df.columns if 'symbol' in c.lower()][0]
symbols = symbols_df[symbol_col].str.strip().tolist()
symbols = [s + ".NS" for s in symbols]

# 2) Batch download 3 months daily data
data = yf.download(
    tickers=" ".join(symbols),
    period="3mo",
    interval="1d",
    group_by="ticker",
    threads=True,
    progress=False
)

selected = []
for sym in symbols:
    df = data.get(sym)
    if df is None or df.empty or len(df) < 50:
        continue

    # 3) Indicators via pandas_ta method-chain
    df["EMA_20"]      = df.ta.ema(length=20)
    df["EMA_50"]      = df.ta.ema(length=50)
    df["RSI"]         = df.ta.rsi(length=14)
    macd_df           = df.ta.macd(fast=12, slow=26, signal=9)
    df["MACD_Line"]   = macd_df["MACD_12_26_9"]
    df["MACD_Signal"] = macd_df["MACDs_12_26_9"]
    df["Vol_SMA_20"]  = df["Volume"].rolling(20).mean()

    latest   = df.iloc[-1]
    prev     = df.iloc[-2]

    # 4) Swing-trade filters
    if (
        latest["Close"]      > latest["EMA_20"]
        and latest["Close"]  > latest["EMA_50"]
        and latest["EMA_20"] > latest["EMA_50"]
        and 50              < latest["RSI"] < 70
        and latest["MACD_Line"] > latest["MACD_Signal"]
        and latest["Volume"]    > latest["Vol_SMA_20"]
        and latest["Close"]     > latest["Open"]
        and latest["Close"]     > prev["Close"]
        and latest["Close"]     > 50
    ):
        selected.append(sym.replace(".NS",""))

# 5) Print results
print("🎯 Matching stocks:", selected)
