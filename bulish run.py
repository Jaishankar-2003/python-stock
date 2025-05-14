import pandas as pd
import yfinance as yf
import numpy as np

# === Load and Fix Stock Symbols ===
try:
    stock_data = pd.read_csv("filtered_stock_names.csv", header=None, names=['SYMBOL'])  # Force SYMBOL as column name
    stock_data['SYMBOL'] = stock_data['SYMBOL'].astype(str).str.upper() + ".NS"
except Exception as e:
    print(f"Error loading stock data: {e}")
    exit()


# === Helper: Fetch historical stock data ===
def fetch_data(symbol):
    try:
        data = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if data.empty:
            print(f"No data available for {symbol}.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


# === Helper: Compute RSI manually ===
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# === Helper: Compute MACD ===
def compute_macd(data, fast_period=12, slow_period=26, signal_period=9):
    fast_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal


# === Fundamental Filter ===
def filter_fundamentals(symbol):
    try:
        info = yf.Ticker(symbol).info
        market_cap = info.get("marketCap", 0)
        debt_to_equity = info.get("debtToEquity", 1.5)
        eps = info.get("trailingEPS", 0)
        roe = info.get("returnOnEquity", 0)

        if market_cap > 1000000000 and eps > 0 and roe is not None and roe > 0:
            return True
        else:
            print(f"{symbol} failed fundamental filter (Market Cap: {market_cap}, EPS: {eps}, ROE: {roe}).")
            return False
    except Exception as e:
        print(f"Error in fundamental data for {symbol}: {e}")
        return False


# === Technical Filter ===
def apply_technical_indicators(symbol):
    data = fetch_data(symbol)
    if data is None:
        return False

    try:
        data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
        data['RSI'] = compute_rsi(data['Close'])
        data['MACD'], data['MACD_Signal'] = compute_macd(data)

        data['SMA20'] = data['Close'].rolling(window=20).mean()
        current_volume = data['Volume'].iloc[-1]
        avg_volume_20 = data['Volume'].rolling(window=20).mean().iloc[-1]

        ema_condition = data['EMA50'].iloc[-1] > data['EMA200'].iloc[-1]
        rsi_condition = 30 < data['RSI'].iloc[-1] < 70
        macd_condition = data['MACD'].iloc[-1] > data['MACD_Signal'].iloc[-1]
        sma_condition = data['Close'].iloc[-1] > data['SMA20'].iloc[-1]
        volume_condition = current_volume > avg_volume_20

        if ema_condition and rsi_condition and macd_condition and sma_condition and volume_condition:
            return True
        else:
            print(
                f"{symbol} failed technical filter (EMA50: {data['EMA50'].iloc[-1]}, EMA200: {data['EMA200'].iloc[-1]}, "
                f"RSI: {data['RSI'].iloc[-1]}, MACD: {data['MACD'].iloc[-1]}, MACD_Signal: {data['MACD_Signal'].iloc[-1]}, "
                f"Volume: {current_volume}, AvgVolume20: {avg_volume_20}, SMA20: {data['SMA20'].iloc[-1]}).")
            return False
    except Exception as e:
        print(f"Error calculating indicators for {symbol}: {e}")
        return False


# === Historical Performance Filter ===
def check_historical_performance(symbol):
    data = fetch_data(symbol)
    if data is None:
        return False

    try:
        data['5d_change'] = (data['Close'] / data['Close'].shift(5) - 1) * 100
        data['10d_change'] = (data['Close'] / data['Close'].shift(10) - 1) * 100

        if data['5d_change'].iloc[-1] > 5 and data['10d_change'].iloc[-1] > 10:
            return True
        else:
            print(
                f"{symbol} failed historical performance filter (5d: {data['5d_change'].iloc[-1]}, 10d: {data['10d_change'].iloc[-1]}).")
            return False
    except Exception as e:
        print(f"Error calculating historical performance for {symbol}: {e}")
        return False


# === Main: Filter Stocks ===
def filter_stocks(stock_data):
    selected = []
    failed_stocks = []
    total = len(stock_data)

    for index, symbol in enumerate(stock_data['SYMBOL']):
        print(f"\n[{index+1}/{total}] Checking {symbol}...")
        if filter_fundamentals(symbol) and apply_technical_indicators(symbol) and check_historical_performance(symbol):
            print(f"✅ {symbol} passed all filters.")
            selected.append(symbol)
        else:
            print(f"❌ {symbol} did not pass the criteria.")
            failed_stocks.append(symbol)

    return selected, failed_stocks


# === Run the filter ===
selected_stocks, failed_stocks = filter_stocks(stock_data)

# === Output results ===
print("\n✅ Final Summary:")
print(f"Total Checked: {len(stock_data)}")
print(f"Passed: {len(selected_stocks)}")
print(f"Failed: {len(failed_stocks)}")

# Save to CSV
pd.DataFrame(selected_stocks, columns=["SYMBOL"]).to_csv("selected_stocks.csv", index=False)
pd.DataFrame(failed_stocks, columns=["SYMBOL"]).to_csv("failed_stocks.csv", index=False)

print("\n📁 Results saved to 'selected_stocks.csv' and 'failed_stocks.csv'")
