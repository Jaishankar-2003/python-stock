import pandas as pd
import numpy as np
import glob

# =========================================================
# CONFIG
# =========================================================
ATR_PERIOD = 14
VOL_AVG_PERIOD = 20

# Split detection settings (safe)
SPLIT_RATIO_TRIGGER = 1.8  # detect only large drops
ALLOWED_RATIOS = np.array([2, 3, 4, 5, 10])  # safe split ratios
RATIO_TOLERANCE = 0.08  # 8% tolerance for noise

# =========================================================
# HELPERS
# =========================================================
def clean_numeric_column(col):
    return pd.to_numeric(col.astype(str).str.replace(",", "").str.strip(), errors="coerce")


def snap_to_allowed_ratio(ratio):
    """
    Snap ratio to nearest allowed split ratio if within tolerance.
    Example:
      9.95 -> 10
      1.92 -> 2
      4.1  -> 4
    """
    nearest = ALLOWED_RATIOS[np.argmin(np.abs(ALLOWED_RATIOS - ratio))]
    if abs(ratio - nearest) / nearest <= RATIO_TOLERANCE:
        return float(nearest)
    return None


# =========================================================
# SAFE SPLIT / BONUS ADJUSTMENT
# =========================================================
def safe_auto_adjust_splits(df, ratio_trigger=SPLIT_RATIO_TRIGGER):
    """
    Detects real split/bonus events safely.
    Prevents false detection from normal gap-down.

    Conditions for split:
    1) Close ratio must be big: prev_close / today_close > ratio_trigger
    2) Ratio must match allowed ratios: 2,3,4,5,10 (with tolerance)
    3) Confirm using OHLC (not only close)
    """

    df = df.copy().reset_index(drop=True)

    close = df["Close"].astype(float)
    open_ = df["Open"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)

    split_events = []

    for i in range(1, len(df)):
        prev_close = close.iloc[i - 1]
        today_close = close.iloc[i]

        if prev_close <= 0 or today_close <= 0:
            continue

        ratio = prev_close / today_close

        # 1) Must be large drop
        if ratio < ratio_trigger:
            continue

        # 2) Must match real split ratios
        used_ratio = snap_to_allowed_ratio(ratio)
        if used_ratio is None:
            continue

        # 3) Confirm with OHLC ratios
        # If it is a split, OPEN/HIGH/LOW also should scale similarly
        open_ratio = prev_close / open_.iloc[i] if open_.iloc[i] > 0 else np.nan
        high_ratio = prev_close / high.iloc[i] if high.iloc[i] > 0 else np.nan
        low_ratio = prev_close / low.iloc[i] if low.iloc[i] > 0 else np.nan

        ratios = np.array([ratio, open_ratio, high_ratio, low_ratio])
        ratios = ratios[~np.isnan(ratios)]

        # If ratios are not consistent, it's likely a normal crash
        if np.std(ratios) > 0.6:
            continue

        # ✅ Confirmed split event
        split_events.append({
            "index": i,
            "raw_ratio": ratio,
            "used_ratio": used_ratio,
            "prev_close": prev_close,
            "today_close": today_close
        })

        # Adjust all older candles
        df.loc[:i - 1, ["Open", "High", "Low", "Close"]] = (
            df.loc[:i - 1, ["Open", "High", "Low", "Close"]] / used_ratio
        )

        # Volume should multiply
        df.loc[:i - 1, "Volume"] = df.loc[:i - 1, "Volume"] * used_ratio

        # Refresh arrays after adjustment
        close = df["Close"].astype(float)
        open_ = df["Open"].astype(float)
        high = df["High"].astype(float)
        low = df["Low"].astype(float)

    return df, split_events


# =========================================================
# ATR (WILDER) + VOLATILITY
# =========================================================
def add_atr(df, period=ATR_PERIOD):
    prev_close = df["Close"].shift(1)

    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - prev_close).abs()
    tr3 = (df["Low"] - prev_close).abs()

    df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Wilder ATR
    df["ATR"] = df["TR"].ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    return df


# =========================================================
# MAIN ANALYSIS FUNCTION
# =========================================================
def analyze_volatility_from_csv(file_path):
    df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = [col.strip().lower() for col in df.columns]

    # Column mapping
    column_map = {}
    for col in df.columns:
        if "open" in col and "prev" not in col:
            column_map["Open"] = col
        elif "high" in col:
            column_map["High"] = col
        elif "low" in col:
            column_map["Low"] = col
        elif "prev" in col:
            column_map["Prev Close"] = col
        elif "close" in col and "prev" not in col:
            column_map["Close"] = col
        elif "date" in col:
            column_map["Date"] = col
        elif "vol" in col:
            column_map["Volume"] = col

    required = ["Open", "High", "Low", "Prev Close", "Close", "Date", "Volume"]
    for req in required:
        if req not in column_map:
            print(f"❌ Error: Couldn't detect column for '{req}' in {file_path}")
            return

    # Rename
    df = df.rename(columns={v: k for k, v in column_map.items()})

    # Convert dates
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%Y", errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

    # Clean numeric
    for col in ["Open", "High", "Low", "Prev Close", "Close", "Volume"]:
        df[col] = clean_numeric_column(df[col])

    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"]).reset_index(drop=True)

    # =========================================================
    # ✅ SAFE SPLIT ADJUSTMENT
    # =========================================================
    df, split_events = safe_auto_adjust_splits(df)

    if split_events:
        print("\n✅ Split/Bonus Detected & Adjusted (SAFE MODE):")
        for e in split_events:
            print(
                f" - Index {e['index']} | Ratio {e['raw_ratio']:.2f} → Used {e['used_ratio']} "
                f"| PrevClose {e['prev_close']:.2f} → TodayClose {e['today_close']:.2f}"
            )

    # =========================================================
    # ✅ ATR + Volatility
    # =========================================================
    df = add_atr(df)

    # Volume avg
    df["VolumeAvg20"] = df["Volume"].rolling(window=VOL_AVG_PERIOD).mean()

    latest = df.iloc[-1]
    latest_close = latest["Close"]
    latest_atr = latest["ATR"]
    latest_volume = latest["Volume"]
    avg_volume = latest["VolumeAvg20"]

    if pd.isna(latest_atr) or pd.isna(avg_volume):
        print("⚠️ Not enough data for ATR/VolumeAvg.")
        return

    # ATR %
    volatility_pct = (latest_atr / latest_close) * 100

    # Volatility sentiment
    if volatility_pct < 5:
        vol_sentiment = "🟢 Low volatility - stable swing moves"
    elif 5 <= volatility_pct <= 10:
        vol_sentiment = "🟠 Moderate volatility - normal swing risk"
    else:
        vol_sentiment = "🔴 High volatility - risky, big SL needed"

    # Volume spike
    volume_spike = latest_volume > 1.5 * avg_volume
    volume_sentiment = "📈 Volume Spike Detected!" if volume_spike else "📉 Volume Normal"

    # Swing stoploss idea
    swing_stop = latest_close - (latest_atr * 1.5)

    # Normal daily range (ATR band)
    range_low = latest_close - latest_atr
    range_high = latest_close + latest_atr

    # Swing stop components
    swing_risk = latest_atr * 1.5

    print(f"\n📌 Latest Close: ₹{latest_close:.2f}")
    print(f"📌 ATR(14) Wilder: ₹{latest_atr:.2f}")
    print(f"📌 Volatility: {volatility_pct:.2f}%")
    print(f"📌 Volatility Sentiment: {vol_sentiment}")
    print(f"📌 Latest Volume: {latest_volume:,.0f}")
    print(f"📌 20D Avg Volume: {avg_volume:,.0f}")
    print(f"📌 Volume Sentiment: {volume_sentiment}")

    print(f"\n📊 Normal Daily Range:")
    print(f"₹{latest_close:.2f} ± ₹{latest_atr:.2f}")
    print(f"≈ ₹{range_low:.2f} to ₹{range_high:.2f}")

    print(f"\n🛑 Swing Stop Calculation:")
    print(f"Close - (ATR × 1.5)")
    print(f"{latest_close:.2f} - ({latest_atr:.2f} × 1.5)")
    print(f"= {latest_close:.2f} - {swing_risk:.2f}")
    print(f"= ₹{swing_stop:.2f}")


# =========================================================
# RUN ALL CSV FILES
# =========================================================
if __name__ == "__main__":
    folder_path = "/home/sri-jaya-shankaran/PycharmProjects/stock/csv file/*.csv"
    csv_files = glob.glob(folder_path)

    if not csv_files:
        print("❌ No CSV files found.")
    else:
        for file_path in csv_files:
            print("\n===================================================")
            print("Processing:", file_path)
            analyze_volatility_from_csv(file_path)