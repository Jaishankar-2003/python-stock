import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

LOOKBACK = 20
RSI_PERIOD = 14
ATR_PERIOD = 14

INITIAL_CAPITAL = 100_000
RISK_PER_TRADE = 0.01          # 1% risk
MIN_TRADES_REQUIRED = 30       # statistical validity

REQUIRED_COLUMNS = {"OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"}

# =========================================================
# DATA CLEANING (NSE SAFE)
# =========================================================

def clean_numeric_columns(df):
    for col in df.columns:
        if col.upper() in ["OPEN", "HIGH", "LOW", "CLOSE", "LTP", "VWAP", "VOLUME", "VALUE"]:
            df[col] = (
                df[col].astype(str)
                .str.replace(",", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def load_csv(csv_file):
    df = pd.read_csv(csv_file)
    df = clean_numeric_columns(df)

    if "DATE" in df.columns:
        df["DATE"] = pd.to_datetime(df["DATE"], format="%d-%b-%Y", errors="coerce")
        df = df.sort_values("DATE")
        df = df.reset_index(drop=True)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df

# =========================================================
# SAFETY
# =========================================================

def has_minimum_data(df):
    return len(df) >= max(LOOKBACK + 1, RSI_PERIOD + 1, 50)

# =========================================================
# INDICATORS
# =========================================================

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def rsi(series, period=RSI_PERIOD):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    gain_ema = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    loss_ema = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    rs = gain_ema / loss_ema.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def atr(df, period=ATR_PERIOD):
    tr = pd.concat([
        df["HIGH"] - df["LOW"],
        (df["HIGH"] - df["CLOSE"].shift()).abs(),
        (df["LOW"] - df["CLOSE"].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def add_indicators(df):
    df = df.copy()
    df["EMA20"] = ema(df["CLOSE"], 20)
    df["EMA50"] = ema(df["CLOSE"], 50)
    df["RSI"] = rsi(df["CLOSE"])
    df["ATR"] = atr(df)
    df["AvgVol20"] = df["VOLUME"].rolling(20).mean()
    return df

# =========================================================
# STRATEGY LOGIC
# =========================================================

def evaluate_conditions(row, prev_high):
    breakout = row["CLOSE"] > prev_high
    near_breakout = prev_high * 0.99 < row["CLOSE"] <= prev_high
    vol_ok = row["VOLUME"] > 1.5 * row["AvgVol20"]
    trend_ok = row["CLOSE"] > row["EMA20"] > row["EMA50"]
    rsi_ok = 50 <= row["RSI"] <= 75
    return breakout, near_breakout, vol_ok, trend_ok, rsi_ok

# =========================================================
# POSITION & RISK
# =========================================================

def calculate_position_size(capital, entry, stop):
    risk_amt = capital * RISK_PER_TRADE
    risk_per_share = abs(entry - stop)
    if risk_per_share == 0:
        return 0
    return int(risk_amt // risk_per_share)

def calculate_drawdown(equity_curve):
    equity = pd.Series(equity_curve)
    peak = equity.cummax()
    return (equity - peak) / peak

# =========================================================
# SINGLE STOCK BACKTEST
# =========================================================

def backtest_strategy(df):
    if not has_minimum_data(df):
        return None

    df = add_indicators(df)

    capital = INITIAL_CAPITAL
    equity_curve = [capital]
    trades = []

    for i in range(LOOKBACK + 1, len(df) - 1):
        row = df.iloc[i]

        if pd.isna(row["RSI"]) or pd.isna(row["ATR"]):
            continue

        prev_high = df["HIGH"].iloc[i - LOOKBACK:i].max()
        breakout, _, vol_ok, trend_ok, rsi_ok = evaluate_conditions(row, prev_high)

        if breakout and vol_ok and trend_ok and rsi_ok:
            entry = row["CLOSE"]
            stop = entry - 1.5 * row["ATR"]
            target = entry + 2 * row["ATR"]

            qty = calculate_position_size(capital, entry, stop)
            if qty <= 0:
                continue

            for j in range(i + 1, len(df)):
                high = df.iloc[j]["HIGH"]
                low = df.iloc[j]["LOW"]

                if high >= target:
                    pnl = qty * (target - entry)
                    capital += pnl
                    trades.append(pnl)
                    equity_curve.append(capital)
                    break

                if low <= stop:
                    pnl = qty * (stop - entry)
                    capital += pnl
                    trades.append(pnl)
                    equity_curve.append(capital)
                    break

    if not trades:
        return None

    return pd.Series(equity_curve), trades

# =========================================================
# MULTI STOCK BACKTEST (PORTFOLIO)
# =========================================================

def backtest_multiple_stocks(csv_files):
    total_trades = 0
    portfolio_equity = [INITIAL_CAPITAL]
    capital = INITIAL_CAPITAL

    for file in csv_files:
        df = load_csv(file)
        result = backtest_strategy(df)

        if result is None:
            continue

        equity, trades = result
        total_trades += len(trades)
        capital = equity.iloc[-1]
        portfolio_equity.append(capital)

    return total_trades, pd.Series(portfolio_equity)

# =========================================================
# TODAY SIGNAL
# =========================================================

def today_signal(df):
    if not has_minimum_data(df):
        return "NO TRADE"

    df = add_indicators(df)
    last = df.iloc[-1]

    if pd.isna(last["RSI"]):
        return "NO TRADE"

    prev_high = df["HIGH"].iloc[-LOOKBACK-1:-1].max()
    breakout, near_breakout, vol_ok, trend_ok, rsi_ok = evaluate_conditions(last, prev_high)

    if breakout and vol_ok and trend_ok and rsi_ok:
        return "BUY TRIGGER"
    elif near_breakout and trend_ok:
        return "PREPARE"
    return "NO TRADE"

# =========================================================
# FINAL CONCLUSION
# =========================================================

def final_conclusion(signal, total_trades):
    if signal == "BUY TRIGGER" and total_trades >= MIN_TRADES_REQUIRED:
        return "BUY"
    if signal in ["BUY TRIGGER", "PREPARE"]:
        return "WATCH"
    return "IGNORE"

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent

    csv_root = BASE_DIR / "csv file"

    # 🔥 Recursive search for all NSE equity CSVs
    csv_files = list(csv_root.rglob("Quote-Equity-*-EQ-*.csv"))

    if not csv_files:
        raise FileNotFoundError("No NSE CSV files found under csv file/")

    print(f"Found {len(csv_files)} CSV files")

    # =====================================================
    # 1️⃣ PORTFOLIO VALIDATION (ALL STOCKS)
    # =====================================================

    total_trades, portfolio_equity = backtest_multiple_stocks(csv_files)

    statistically_valid = total_trades >= MIN_TRADES_REQUIRED

    print("\n📊 PORTFOLIO VALIDATION")
    print("Total Trades Collected:", total_trades)
    print("Statistically Valid (30+):", statistically_valid)

    # =====================================================
    # 2️⃣ TODAY'S DECISION FOR EACH STOCK
    # =====================================================

    print("\n📌 TODAY'S STOCK DECISIONS")

    results = []

    for csv_file in csv_files:
        df = load_csv(csv_file)

        signal = today_signal(df)
        decision = final_conclusion(signal, total_trades)

        results.append({
            "Stock": csv_file.name,
            "Signal": signal,
            "Conclusion": decision
        })

        print(f"{csv_file.name} | Signal: {signal} | Decision: {decision}")

    # =====================================================
    # 3️⃣ OPTIONAL: SAVE RESULTS
    # =====================================================

    results_df = pd.DataFrame(results)
    results_df.to_csv("daily_swing_decisions.csv", index=False)

    #print("\n✔ Daily decisions saved to daily_swing_decisions.csv")
