
import pandas as pd
import numpy as np
import glob
import os

# =========================================================
# CONFIG
# =========================================================

LOOKBACK = 20
RSI_PERIOD = 14
ATR_PERIOD = 14

STRICTNESS = 0.90

REQUIRED_COLUMNS = {"OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"}

# ✅ STRATEGY FILTERS
BREAKOUT_CONFIRM_PCT = 1.003        # 0.3% above resistance
CLOSE_STRENGTH_LEVEL = 0.70         # close should be in top 30% of candle
RETEST_ZONE_PCT = 0.015             # 1.5% near EMA20/EMA50
TWO_DAY_CONFIRM_NEAR = 0.995        # yesterday close near breakout

# ✅ ATR STOP SETTINGS
ATR_MULT_EARLY = 2.0
ATR_MULT_CONFIRM = 1.5
ATR_MULT_RETEST = 1.8

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
                .str.replace("₹", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def detect_date_column(df):
    possible = ["DATE", "Date", "TIMESTAMP", "Timestamp", "date", "timestamp"]
    for c in possible:
        if c in df.columns:
            return c
    return None


# =========================================================
# AUTO SPLIT / BONUS ADJUSTMENT (NEW)
# =========================================================

def auto_adjust_splits(
    df,
    price_cols=("OPEN", "HIGH", "LOW", "CLOSE"),
    volume_col="VOLUME",
    ratio_trigger=1.8,
):
    """
    Auto-detects split/bonus like corporate actions from raw NSE historical data
    and adjusts older candles to match latest price scale.

    Example:
      prev_close = 8400
      today_close = 1050
      ratio = 8400/1050 = 8  -> split/bonus factor

    What it does:
    - Adjusts older prices by dividing by factor
    - Adjusts older volume by multiplying by factor
    - Supports multiple split events
    """

    df = df.copy().reset_index(drop=True)

    # Must be oldest -> newest
    # (load_csv sorts by date already)
    close = df["CLOSE"].astype(float)

    ratio = close.shift(1) / close

    # Detect only big down-jumps (typical split/bonus)
    events = df[ratio > ratio_trigger].copy()

    if events.empty:
        return df, []

    split_events = []

    # common ratios (snap to nearest to avoid noise)
    common = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 1.5, 1.25])

    def snap_ratio(x):
        idx = int(np.argmin(np.abs(common - x)))
        return float(common[idx])

    # process events oldest -> newest
    for idx in events.index:
        r = ratio.loc[idx]
        if pd.isna(r) or r <= 0:
            continue

        used = snap_ratio(r)

        split_events.append({
            "index": int(idx),
            "raw_ratio": float(r),
            "used_ratio": float(used),
            "prev_close": float(close.shift(1).loc[idx]),
            "today_close": float(close.loc[idx]),
        })

        # adjust ALL older candles
        df.loc[:idx-1, list(price_cols)] = df.loc[:idx-1, list(price_cols)] / used

        if volume_col in df.columns:
            df.loc[:idx-1, volume_col] = df.loc[:idx-1, volume_col] * used

        # refresh close + ratio for multiple events
        close = df["CLOSE"].astype(float)
        ratio = close.shift(1) / close

    return df, split_events


def load_csv(csv_file):
    df = pd.read_csv(csv_file)
    df.columns = [c.strip() for c in df.columns]

    date_col = detect_date_column(df)

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
        df = df.dropna(subset=[date_col])
        df = df.sort_values(date_col).reset_index(drop=True)
    else:
        print("⚠️ WARNING: No DATE column found. Indicators may be wrong if CSV is reversed.")

    df = clean_numeric_columns(df)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.dropna(subset=["CLOSE", "HIGH", "LOW", "OPEN", "VOLUME"]).reset_index(drop=True)

    # ✅ NEW: Auto adjust split/bonus
    df, split_events = auto_adjust_splits(df)

    if split_events:
        print("\n✅ Split/Bonus Detected & Adjusted:")
        for e in split_events:
            print(
                f" - Index {e['index']} | Ratio {e['raw_ratio']:.2f} → Used {e['used_ratio']} "
                f"| PrevClose {e['prev_close']:.2f} → TodayClose {e['today_close']:.2f}"
            )

    return df


# =========================================================
# INDICATORS
# =========================================================

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def rsi_wilder(series, period=RSI_PERIOD):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.where(avg_loss != 0, 100)
    rsi = rsi.where(avg_gain != 0, 0)

    return rsi


def atr(df, period=ATR_PERIOD):
    high = df["HIGH"]
    low = df["LOW"]
    close = df["CLOSE"]

    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_val = true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    return atr_val


def add_indicators(df):
    df = df.copy()

    df["EMA20"] = ema(df["CLOSE"], 20)
    df["EMA50"] = ema(df["CLOSE"], 50)
    df["EMA200"] = ema(df["CLOSE"], 200)

    df["RSI_WILDER"] = rsi_wilder(df["CLOSE"], RSI_PERIOD)

    df["AvgVol20"] = df["VOLUME"].rolling(20).mean()

    df["ATR14"] = atr(df, ATR_PERIOD)

    return df


# =========================================================
# STRICTNESS / SCORING SYSTEM
# =========================================================

def strictness_required_score(strictness: float) -> int:
    return 4 if strictness >= 0.95 else 3


def get_liberal_params(strictness: float):
    if strictness >= 0.95:
        return {"vol_multiplier": 1.5, "rsi_low": 50, "rsi_high": 75, "near_breakout_pct": 0.99}

    if strictness >= 0.90:
        return {"vol_multiplier": 1.2, "rsi_low": 48, "rsi_high": 78, "near_breakout_pct": 0.985}

    return {"vol_multiplier": 1.0, "rsi_low": 45, "rsi_high": 80, "near_breakout_pct": 0.98}


# =========================================================
# STRATEGY LOGIC
# =========================================================

def evaluate_conditions(row, prev_high, params):
    breakout = row["CLOSE"] > prev_high * BREAKOUT_CONFIRM_PCT
    near_breakout = row["CLOSE"] > prev_high * params["near_breakout_pct"]

    vol_ok = row["VOLUME"] > params["vol_multiplier"] * row["AvgVol20"]

    early_trend_ok = (row["EMA20"] > row["EMA50"]) and (row["CLOSE"] > row["EMA50"])
    ema200_ok = row["CLOSE"] > row["EMA200"]

    rsi_val = row["RSI_WILDER"]
    rsi_ok = params["rsi_low"] <= rsi_val <= params["rsi_high"]

    candle_range = row["HIGH"] - row["LOW"]
    if candle_range <= 0:
        close_strong = False
    else:
        close_strong = row["CLOSE"] > (row["LOW"] + CLOSE_STRENGTH_LEVEL * candle_range)

    near_ema20 = abs(row["CLOSE"] - row["EMA20"]) / row["EMA20"] <= RETEST_ZONE_PCT
    near_ema50 = abs(row["CLOSE"] - row["EMA50"]) / row["EMA50"] <= RETEST_ZONE_PCT
    retest_zone = near_ema20 or near_ema50

    return breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok, close_strong, retest_zone


# =========================================================
# 2-DAY BREAKOUT CONFIRMATION
# =========================================================

def two_day_breakout_confirm(df, lookback=LOOKBACK):
    if len(df) < lookback + 3:
        return False

    today = df.iloc[-1]
    yesterday = df.iloc[-2]

    prev_high = df["HIGH"].iloc[-lookback-2:-2].max()

    today_breakout = today["CLOSE"] > prev_high * BREAKOUT_CONFIRM_PCT
    yesterday_near = yesterday["CLOSE"] > prev_high * TWO_DAY_CONFIRM_NEAR

    return bool(today_breakout and yesterday_near)


# =========================================================
# ENTRY RULES
# =========================================================

def should_buy_signal(
    breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok,
    rsi_ok, close_strong, retest_zone,
    score, required,
    confirm_2day
):

    # CONFIRM BUY
    if breakout and ema200_ok and score >= required and close_strong and confirm_2day:
        return True, "CONFIRM_BUY"

    # EARLY BUY
    if breakout and early_trend_ok and vol_ok and rsi_ok and close_strong:
        return True, "EARLY_BUY"

    # RETEST BUY
    if retest_zone and early_trend_ok and vol_ok and close_strong and rsi_ok:
        return True, "RETEST_BUY"

    # PREPARE
    if near_breakout and early_trend_ok and (vol_ok or rsi_ok):
        return True, "PREPARE"

    return False, None


# =========================================================
# ATR STOP CALCULATION
# =========================================================

def atr_stop_price(close, atr_value, signal):
    if pd.isna(atr_value) or atr_value <= 0:
        return None

    if signal == "EARLY_BUY":
        mult = ATR_MULT_EARLY
    elif signal == "CONFIRM_BUY":
        mult = ATR_MULT_CONFIRM
    elif signal == "RETEST_BUY":
        mult = ATR_MULT_RETEST
    else:
        return None

    return close - (atr_value * mult)


# =========================================================
# SIGNAL
# =========================================================

def technical_signal(df, lookback=LOOKBACK, strictness=STRICTNESS):
    df = add_indicators(df)
    last = df.iloc[-1]

    if pd.isna(last["RSI_WILDER"]) or pd.isna(last["EMA50"]) or pd.isna(last["AvgVol20"]):
        return "NO_TRADE"

    params = get_liberal_params(strictness)
    required = strictness_required_score(strictness)

    prev_high = df["HIGH"].iloc[-lookback-1:-1].max()

    breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok, close_strong, retest_zone = evaluate_conditions(
        last, prev_high, params
    )

    conditions = [breakout, vol_ok, early_trend_ok, rsi_ok]
    score = sum(bool(x) for x in conditions)

    confirm_2day = two_day_breakout_confirm(df, lookback)

    buy, reason = should_buy_signal(
        breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok,
        rsi_ok, close_strong, retest_zone,
        score, required,
        confirm_2day
    )

    if not buy:
        return "NO_TRADE"

    return reason


# =========================================================
# DEBUG
# =========================================================

def debug_conditions(df, lookback=LOOKBACK, strictness=STRICTNESS):
    df = add_indicators(df)
    last = df.iloc[-1]

    if pd.isna(last["RSI_WILDER"]):
        print("\n🔍 CONDITION CHECK (LAST CANDLE)")
        print("RSI not ready – insufficient data")
        return

    params = get_liberal_params(strictness)
    required = strictness_required_score(strictness)

    prev_high = df["HIGH"].iloc[-lookback-1:-1].max()

    breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok, close_strong, retest_zone = evaluate_conditions(
        last, prev_high, params
    )

    conditions = [breakout, vol_ok, early_trend_ok, rsi_ok]
    score = sum(bool(x) for x in conditions)

    confirm_2day = two_day_breakout_confirm(df, lookback)

    buy, reason = should_buy_signal(
        breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok,
        rsi_ok, close_strong, retest_zone,
        score, required,
        confirm_2day
    )

    signal = reason if buy else "NO_TRADE"

    atr_val = last["ATR14"]
    atr_stop = atr_stop_price(last["CLOSE"], atr_val, signal)

    print("\n🔍 CONDITION CHECK (LAST CANDLE)")
    print("Strictness Mode:", strictness)
    print("Breakout:", breakout)
    print("Near Breakout:", near_breakout)
    print("Volume Spike:", vol_ok)
    print("Early Trend OK (EMA50):", early_trend_ok)
    print("Above EMA200:", ema200_ok)
    print("RSI OK:", rsi_ok)
    print("Close Strong:", close_strong)
    print("Retest Zone:", retest_zone)
    print("2-Day Confirm (only for CONFIRM_BUY):", confirm_2day)
    print("BUY Logic:", buy, "| Signal:", signal)

    print("\n📌 ATR INFO")
    print("ATR14:", round(atr_val, 2) if not pd.isna(atr_val) else atr_val)
    if atr_stop:
        print("ATR Stop (Recommended):", round(atr_stop, 2))

    print("\n📌 EXTRA INFO")
    print("Close:", last["CLOSE"])
    print("Prev 20D High:", prev_high)
    print("AvgVol20:", round(last["AvgVol20"], 2))
    print("Volume:", last["VOLUME"])
    print("EMA20:", round(last["EMA20"], 2))
    print("EMA50:", round(last["EMA50"], 2))
    print("EMA200:", round(last["EMA200"], 2))


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    csv_paths = glob.glob("csv file/*.csv")

    for csv_path in csv_paths:
        print(f"\nProcessing: {csv_path}")

        df = load_csv(csv_path)

        debug_conditions(df)
        signal = technical_signal(df)

        print("Signal:", signal)
        print("==================================================================")
