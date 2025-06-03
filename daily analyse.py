import pandas as pd
import pandas_ta as ta
import os

# File paths
historical_file = "files/NIFTY MIDCAP150 MOMENTUM 50_his.csv"
current_file = "files/NIFTY-QUALITY-LOW-VOLATILITY-today.csv"

# --- Part 1: EMA Bullish Screening from Historical Data ---
if os.path.exists(historical_file):
    df_hist = pd.read_csv(historical_file)
    df_hist.columns = df_hist.columns.str.strip().str.replace('\n', '', regex=True)

    # Rename columns to standardize
    df_hist.rename(columns={
        'Index Name': 'SYMBOL',
        'Date': 'DATE',
        'Open': 'OPEN',
        'High': 'HIGH',
        'Low': 'LOW',
        'Close': 'CLOSE'
    }, inplace=True)

    # Ensure price columns are numeric
    for col in ['OPEN', 'HIGH', 'LOW', 'CLOSE']:
        df_hist[col] = pd.to_numeric(df_hist[col].astype(str).str.replace(',', ''), errors='coerce')

    bullish_ema_stocks = []

    for symbol in df_hist['SYMBOL'].unique():
        stock_data = df_hist[df_hist['SYMBOL'] == symbol].sort_values('DATE')

        if len(stock_data) < 30:
            continue

        stock_data['EMA_8'] = ta.ema(stock_data['CLOSE'], length=8)
        stock_data['EMA_21'] = ta.ema(stock_data['CLOSE'], length=21)

        if stock_data['EMA_8'].iloc[-1] > stock_data['EMA_21'].iloc[-1]:
            bullish_ema_stocks.append(symbol)

    print("\n📈 EMA Bullish Candidates (8 EMA > 21 EMA):")
    print(bullish_ema_stocks)
else:
    print("\n⚠️ Historical file not found. Skipping EMA-based screening.")

# --- Part 2: Momentum Screening from Current Day File ---
if os.path.exists(current_file):
    df_current = pd.read_csv(current_file)
    df_current.columns = df_current.columns.str.strip().str.replace('\n', '', regex=True).str.replace(' +', ' ', regex=True)

    # Clean numeric columns
    numeric_cols = ['OPEN', 'HIGH', 'LOW', 'PREV. CLOSE', 'LTP', 'CHNG', '%CHNG', 'VOLUME (shares)']
    for col in numeric_cols:
        if col in df_current.columns:
            df_current[col] = pd.to_numeric(df_current[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

    df_current = df_current[df_current['SYMBOL'].notna() & df_current['OPEN'].notna()]

    # Filter bullish current-day stocks
    bullish_df = df_current[(df_current['LTP'] > df_current['PREV. CLOSE']) & (df_current['%CHNG'] > 0)]

    bullish_stocks = bullish_df[['SYMBOL', 'OPEN', 'PREV. CLOSE', 'LTP', 'CHNG', '%CHNG', 'VOLUME (shares)']]
    bullish_stocks = bullish_stocks.sort_values(by='%CHNG', ascending=False)

    print("\n🚀 Momentum Bullish Stocks (Next-Day Candidates):")
    print(bullish_stocks)
else:
    print("\n⚠️ Current day file not found. Skipping momentum-based screening.")
