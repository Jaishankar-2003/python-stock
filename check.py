import os
import pandas as pd


# === Step 1: Select Top 5 Momentum Stocks from Today ===
def get_top_5_bullish_stocks(current_file):
    df = pd.read_csv(current_file)
    df.columns = df.columns.str.strip().str.replace('\n', '', regex=True).str.replace(' +', ' ', regex=True)

    numeric_cols = ['OPEN', 'HIGH', 'LOW', 'PREV. CLOSE', 'LTP', 'CHNG', '%CHNG', 'VOLUME (shares)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

    df = df[df['SYMBOL'].notna() & df['OPEN'].notna()]
    bullish_df = df[(df['LTP'] > df['PREV. CLOSE']) & (df['%CHNG'] > 0)]
    top_5 = bullish_df.sort_values(by='%CHNG', ascending=False).head(5)

    print("\n🚀 Top 5 Momentum Stocks:")
    print(top_5[['SYMBOL', 'LTP', '%CHNG']])
    return top_5['SYMBOL'].tolist()


# === Step 2: Volatility Analysis on Each Stock ===
def analyze_volatility(stock, historical_folder='historical'):
    file_path = os.path.join(historical_folder, f"{stock}.csv")
    if not os.path.exists(file_path):
        print(f"⚠️ Historical file for {stock} not found: {file_path}")
        return

    df = pd.read_csv(file_path)
    df.columns = [col.strip().lower() for col in df.columns]

    try:
        df = df.rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low',
            'close': 'Close', 'previous close': 'Prev Close',
            'date': 'Date', 'volume': 'Volume'
        })

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values('Date')

        for col in ['Open', 'High', 'Low', 'Close', 'Prev Close', 'Volume']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

        df['TR'] = df[['High', 'Prev Close']].max(axis=1) - df[['Low', 'Prev Close']].min(axis=1)
        df['ATR'] = df['TR'].rolling(window=14).mean()
        df['VolumeAvg20'] = df['Volume'].rolling(window=20).mean()

        latest = df.iloc[-1]
        volatility_pct = (latest['ATR'] / latest['Close']) * 100 if pd.notna(latest['ATR']) else None
        volume_spike = latest['Volume'] > 1.5 * latest['VolumeAvg20'] if pd.notna(latest['VolumeAvg20']) else False

        print(f"\n📊 {stock} Analysis:")
        print(f"Close: ₹{latest['Close']:.2f}, ATR: ₹{latest['ATR']:.2f}, Volatility: {volatility_pct:.2f}%")
        print("Volatility Sentiment:",
              "🟢 Low" if volatility_pct < 5 else "🟠 Medium" if volatility_pct < 10 else "🔴 High")
        print("Volume Sentiment:", "📈 Spike" if volume_spike else "📉 Normal")
    except Exception as e:
        print(f"❌ Error processing {stock}: {e}")

        print("Available columns:", df.columns.tolist())


# === Main ===
if __name__ == "__main__":
    today_file = "files/NIFTY-QUALITY-LOW-VOLATILITY-today.csv"
    top_5_symbols = get_top_5_bullish_stocks(today_file)

    for symbol in top_5_symbols:
        analyze_volatility(symbol, historical_folder='historical')
