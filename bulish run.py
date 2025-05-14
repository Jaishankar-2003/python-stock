import pandas as pd
import yfinance as yf
import numpy as np


# === Helper: Fetch historical stock data ===
def fetch_data(symbol):
    try:
        data = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if data.empty or 'Close' not in data.columns or data['Close'].isnull().all():
            print(f"No valid 'Close' data for {symbol}. Skipping.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


# === Helper: Compute RSI (Simplified) ===
def compute_rsi(series, period=14):
    if not isinstance(series, pd.Series):
        series = pd.Series(series)
    if len(series) < period + 1:
        return pd.Series([np.nan] * len(series))
    # A very basic RSI approximation (for debugging)
    rsi = series.rolling(window=period).mean()
    return rsi


# === Helper: Compute MACD (Simplified) ===
def compute_macd(data, fast_period=12, slow_period=26, signal_period=9):
    if 'Close' not in data.columns or len(data) < slow_period:
        return pd.Series([np.nan] * len(data)), pd.Series([np.nan] * len(data))
    # Very basic MACD approximation (for debugging)
    macd = data['Close'].rolling(window=fast_period).mean() - data['Close'].rolling(window=slow_period).mean()
    signal = macd.rolling(window=signal_period).mean()
    return macd, signal


# === Technical Filter ===
def apply_technical_indicators(symbol):
    data = fetch_data(symbol)
    if data is None or data.empty:
        return False

    try:
        if 'Close' not in data.columns or data['Close'].isnull().all():
            print(f"Invalid 'Close' data for {symbol}. Skipping.")
            return False
        if 'Volume' not in data.columns or data['Volume'].isnull().all():
            print(f"Invalid 'Volume' data for {symbol}. Skipping.")
            return False

        data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
        data['RSI'] = compute_rsi(data['Close'])
        data['MACD'], data['MACD_Signal'] = compute_macd(data)
        data['SMA20'] = data['Close'].rolling(window=20).mean()

        def get_last_value(series):
            return series.iloc[-1] if isinstance(series, pd.Series) and not series.empty else np.nan

        ema50_last = get_last_value(data['EMA50'])
        ema200_last = get_last_value(data['EMA200'])
        rsi_last = get_last_value(data['RSI'])
        macd_last = get_last_value(data['MACD'])
        macd_signal_last = get_last_value(data['MACD_Signal'])
        sma20_last = get_last_value(data['SMA20'])
        close_last = get_last_value(data['Close'])
        current_volume = get_last_value(data['Volume'])
        avg_volume_20 = get_last_value(data['SMA20'])  # potential error

        ema_condition = ema50_last > ema200_last if pd.notna(ema50_last) and pd.notna(ema200_last) else False
        rsi_condition = 30 < rsi_last < 70 if pd.notna(rsi_last) else False
        macd_condition = macd_last > macd_signal_last if pd.notna(macd_last) and pd.notna(macd_signal_last) else False
        sma_condition = close_last > sma20_last if pd.notna(close_last) and pd.notna(sma20_last) else False
        volume_condition = current_volume > avg_volume_20 if pd.notna(current_volume) and pd.notna(avg_volume_20) else False

        if ema_condition and rsi_condition and macd_condition and sma_condition and volume_condition:
            return True
        else:
            print(
                f"{symbol} failed: EMA50={ema50_last}, EMA200={ema200_last}, RSI={rsi_last}, MACD={macd_last}, Signal={macd_signal_last}, "
                f"Close={close_last}, SMA20={sma20_last}, Vol={current_volume}, AvgVol20={avg_volume_20}"
            )
            return False

    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return False


# === Main: Filter Stocks ===
def filter_stocks(stock_data):
    selected = []
    failed_stocks = []
    total = len(stock_data)
    for index, symbol in enumerate(stock_data['SYMBOL']):
        print(f"\n[{index + 1}/{total}] Checking {symbol}...")
        if apply_technical_indicators(symbol):
            print(f"✅ {symbol} passed")
            selected.append(symbol)
        else:
            print(f"❌ {symbol} failed")
            failed_stocks.append(symbol)
    return selected, failed_stocks


# === Run the filter ===
stock_data = pd.read_csv("data.csv", header=None, names=['SYMBOL'])
stock_data['SYMBOL'] = stock_data['SYMBOL'].astype(str).str.upper() + ".NS"
selected_stocks, failed_stocks = filter_stocks(stock_data)

# === Output results ===
print("\n✅ Final Summary:")
print(f"Total Checked: {len(stock_data)}")
print(f"Passed: {len(selected_stocks)}")
print(f"Failed: {len(failed_stocks)}")

# Save to CSV
pd.DataFrame(selected_stocks, columns=["SYMBOL"]).to_csv("selected_stocks.csv", index=False)
pd.DataFrame(failed_stocks, columns=["SYMBOL"]).to_csv("failed_stocks.csv", index=False)

print("\n📁 Results saved")