import pandas as pd
import numpy as np

# =========================================================
# CONFIG
# =========================================================

LOOKBACK = 20
RSI_PERIOD = 14
TARGET_PCT = 0.05
STOP_PCT = 0.02

REQUIRED_COLUMNS = {"OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"}

# =========================================================
# DATA CLEANING
# =========================================================

def clean_numeric_columns(df):
    numeric_cols = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def load_csv(csv_file):
    df = pd.read_csv(csv_file)
    df = clean_numeric_columns(df)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df

# =========================================================
# INDICATORS
# =========================================================

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def rsi(series, period=RSI_PERIOD):
    delta = series.diff()

    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    gain_ema = pd.Series(gain, index=series.index).ewm(
        alpha=1 / period, adjust=False
    ).mean()

    loss_ema = pd.Series(loss, index=series.index).ewm(
        alpha=1 / period, adjust=False
    ).mean()

    rs = gain_ema / loss_ema
    return 100 - (100 / (1 + rs))

def add_indicators(df):
    df = df.copy()

    df["EMA20"] = ema(df["CLOSE"], 20)
    df["EMA50"] = ema(df["CLOSE"], 50)
    df["RSI"] = rsi(df["CLOSE"])
    df["AvgVol20"] = df["VOLUME"].rolling(20).mean()

    return df

# =========================================================
# STRATEGY LOGIC
# =========================================================

def evaluate_conditions(row, prev_high):
    breakout = row["CLOSE"] > prev_high
    near_breakout = row["CLOSE"] > prev_high * 0.99
    vol_ok = row["VOLUME"] > 1.5 * row["AvgVol20"]
    trend_ok = row["CLOSE"] > row["EMA20"] > row["EMA50"]
    rsi_ok = 50 <= row["RSI"] <= 75

    return breakout, near_breakout, vol_ok, trend_ok, rsi_ok

def technical_signal(df, lookback=LOOKBACK):
    df = add_indicators(df)

    last = df.iloc[-1]
    prev_high = df["HIGH"].iloc[-lookback-1:-1].max()

    breakout, near_breakout, vol_ok, trend_ok, rsi_ok = evaluate_conditions(
        last, prev_high
    )

    if breakout and vol_ok and trend_ok and rsi_ok:
        return "BUY TRIGGER"
    elif near_breakout and trend_ok:
        return "PREPARE"
    else:
        return "NO TRADE"

# =========================================================
# DEBUG
# =========================================================

def debug_conditions(df, lookback=LOOKBACK):
    df = add_indicators(df)

    last = df.iloc[-1]
    prev_high = df["HIGH"].iloc[-lookback-1:-1].max()

    breakout, _, vol_ok, trend_ok, rsi_ok = evaluate_conditions(
        last, prev_high
    )

    print("\n🔍 CONDITION CHECK (LAST CANDLE)")
    print("Breakout:", breakout)
    print("Volume Spike:", vol_ok)
    print("Trend OK:", trend_ok)
    print("RSI OK:", rsi_ok)
    print("RSI Value:", round(last["RSI"], 2))

# =========================================================
# EXPORT
# =========================================================

def export_signal(df, signal, source_file):
    last = df.iloc[-1]

    out = pd.DataFrame([{
        "Stock": source_file.split("/")[-1],
        "Date": df.iloc[-1].get("DATE", ""),
        "Close": last["CLOSE"],
        "Volume": last["VOLUME"],
        "Signal": signal
    }])

    out.to_csv(
        "trade_signals.csv",
        mode="a",
        header=not pd.io.common.file_exists("trade_signals.csv"),
        index=False
    )

    #out.to_excel("trade_signals.xlsx", index=False)
    print("✔ Signal exported")

# =========================================================
# BACKTEST
# =========================================================

def backtest_strategy(df, lookback=LOOKBACK,
                      target_pct=TARGET_PCT,
                      stop_pct=STOP_PCT):

    df = add_indicators(df)
    trades = []

    for i in range(lookback + 1, len(df) - 1):
        row = df.iloc[i]
        prev_high = df["HIGH"].iloc[i-lookback:i].max()

        breakout, _, vol_ok, trend_ok, rsi_ok = evaluate_conditions(
            row, prev_high
        )

        if breakout and vol_ok and trend_ok and rsi_ok:
            entry = row["CLOSE"]
            target = entry * (1 + target_pct)
            stop = entry * (1 - stop_pct)

            for j in range(i + 1, len(df)):
                if df.iloc[j]["HIGH"] >= target:
                    trades.append(1)
                    break
                if df.iloc[j]["LOW"] <= stop:
                    trades.append(0)
                    break

    if not trades:
        print("No trades found in backtest")
        return

    win_rate = sum(trades) / len(trades) * 100

    print("\n📊 BACKTEST RESULT")
    print("Total Trades:", len(trades))
    print("Winning Trades:", sum(trades))
    print("Win Rate:", round(win_rate, 2), "%")

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    csv_path = "csv file/Quote-Equity-RADICO-EQ-01-01-2026-01-02-2026.csv"

    df = load_csv(csv_path)

    debug_conditions(df)

    signal = technical_signal(df)
    print("\nSignal:", signal)

    export_signal(df, signal, csv_path)
    backtest_strategy(df)
