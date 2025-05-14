import pandas as pd
import yfinance as yf
import talib as ta
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


# Function to fetch data from Yahoo Finance
def fetch_data(stock_symbol):
    try:
        data = yf.download(stock_symbol, period="6mo", interval="1d")
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

        # Filter based on the criteria
        if market_cap > 5000 and debt_to_equity < 1 and eps > 0 and roe > 0.1:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error in fundamental data for {stock_symbol}: {e}")
        return False


# Technical indicators
def apply_technical_indicators(stock_symbol):
    data = fetch_data(stock_symbol)
    if data is None:
        return None

    # Calculate RSI
    data['RSI'] = ta.RSI(data['Close'], timeperiod=14)

    # Calculate EMA (50 and 200)
    data['EMA50'] = ta.EMA(data['Close'], timeperiod=50)
    data['EMA200'] = ta.EMA(data['Close'], timeperiod=200)

    # Conditions for technical filters
    if data['RSI'].iloc[-1] > 30 and data['RSI'].iloc[-1] < 70:  # RSI between 30 and 70
        if data['EMA50'].iloc[-1] > data['EMA200'].iloc[-1]:  # EMA 50 > EMA 200
            return True
    return False


# Main filtering function
def filter_stocks(stock_data):
    selected_stocks = []

    for symbol in stock_data['SYMBOL']:
        # Check for both fundamental and technical filters
        if filter_fundamentals(symbol) and apply_technical_indicators(symbol):
            selected_stocks.append(symbol)

    return selected_stocks


# Function to open file dialog and select CSV
def load_csv():
    file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            stock_data = pd.read_csv(file_path)
            if 'SYMBOL' not in stock_data.columns:
                messagebox.showerror("Error", "CSV must contain a 'SYMBOL' column.")
            else:
                selected_stocks = filter_stocks(stock_data)
                if selected_stocks:
                    result_text.set("Selected Stocks: " + ", ".join(selected_stocks))
                else:
                    result_text.set("No stocks met the criteria.")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading CSV: {e}")


# Setup GUI
root = tk.Tk()
root.title("Stock Filter GUI")
root.geometry("600x400")

# Create GUI components
frame = ttk.Frame(root)
frame.pack(pady=20)

load_button = ttk.Button(frame, text="Load CSV File", command=load_csv)
load_button.pack()

result_text = tk.StringVar()
result_label = ttk.Label(root, textvariable=result_text, wraplength=500)
result_label.pack(pady=20)

# Run the GUI
root.mainloop()