import pandas as pd
import yfinance as yf
import ta
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
import numpy as np

# Load your stock list from the CSV
stock_data = pd.read_csv("nifty-50.csv")


# Function to fetch data from Yahoo Finance
def fetch_data(stock_symbol):
    try:
        data = yf.download(stock_symbol, period="6mo", interval="1d", progress=False)
        return data
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {e}")
        return None


# Fundamental filters
def filter_fundamentals(stock_symbol):
    try:
        stock_info = yf.Ticker(stock_symbol).info
        market_cap = stock_info.get("marketCap", 0)
        debt_to_equity = stock_info.get("debtToEquity", 0)
        eps = stock_info.get("trailingEPS", 0)
        roe = stock_info.get("returnOnEquity", 0)

        if market_cap > 5000 and debt_to_equity < 1 and eps > 0 and roe > 0.1:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error in fundamental data for {stock_symbol}: {e}")
        return False


# Technical indicators using 'ta' package
def apply_technical_indicators(stock_symbol):
    data = fetch_data(stock_symbol)
    if data is None or data.empty:
        return False

    try:
        # Calculate RSI
        rsi = RSIIndicator(close=data['Close'], window=14)
        data['RSI'] = rsi.rsi()

        # Calculate EMA 50
        ema_50 = EMAIndicator(close=data['Close'], window=50)
        data['EMA50'] = ema_50.ema_indicator()

        # Calculate EMA 200
        ema_200 = EMAIndicator(close=data['Close'], window=200)
        data['EMA200'] = ema_200.ema_indicator()

        # Drop NaN values
        data.dropna(inplace=True)

        # Conditions
        if data['RSI'].iloc[-1] > 30 and data['RSI'].iloc[-1] < 70:
            if data['EMA50'].iloc[-1] > data['EMA200'].iloc[-1]:
                return True

    except Exception as e:
        print(f"Technical indicator error for {stock_symbol}: {e}")

    return False


# Main filtering function
def filter_stocks(stock_data):
    selected_stocks = []

    for symbol in stock_data['SYMBOL']:
        print(f"Checking {symbol}...")
        if filter_fundamentals(symbol) and apply_technical_indicators(symbol):
            selected_stocks.append(symbol)

    return selected_stocks


# Run the filtering
selected_stocks = filter_stocks(stock_data)

# Output result
if selected_stocks:
    print("\n✅ Stocks that meet the criteria:")
    for stock in selected_stocks:
        print(stock)
else:
    print("\n❌ No stocks met the criteria.")
