import pandas as pd

def clean_numeric_column(col):
    return pd.to_numeric(col.str.replace(',', '').str.strip(), errors='coerce')

def analyze_volatility_from_csv(file_path):
    # Load CSV
    df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = [col.strip().lower() for col in df.columns]
    print("Detected columns:", df.columns.tolist())  # Debug

    # Column mapping
    column_map = {}
    for col in df.columns:
        if 'open' in col and 'prev' not in col:
            column_map['Open'] = col
        elif 'high' in col:
            column_map['High'] = col
        elif 'low' in col:
            column_map['Low'] = col
        elif 'prev' in col:
            column_map['Prev Close'] = col
        elif 'close' in col and 'prev' not in col:
            column_map['Close'] = col
        elif 'date' in col:
            column_map['Date'] = col
        elif 'vol' in col:
            column_map['Volume'] = col

    # Validate required columns
    required = ['Open', 'High', 'Low', 'Prev Close', 'Close', 'Date', 'Volume']
    for req in required:
        if req not in column_map:
            print(f"Error: Couldn't detect column for '{req}'")
            return

    # Rename columns
    df = df.rename(columns={v: k for k, v in column_map.items()})

    # Convert dates
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y', errors='coerce')
    df = df.dropna(subset=['Date']).sort_values('Date').reset_index(drop=True)

    # Clean price and volume columns
    for col in ['Open', 'High', 'Low', 'Prev Close', 'Close', 'Volume']:
        df[col] = clean_numeric_column(df[col].astype(str))

    # True Range & ATR
    df['TR'] = df[['High', 'Prev Close']].max(axis=1) - df[['Low', 'Prev Close']].min(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()

    # Volume Spike Calculation
    df['VolumeAvg20'] = df['Volume'].rolling(window=20).mean()
    latest_volume = df['Volume'].iloc[-1]
    latest_volume_avg = df['VolumeAvg20'].iloc[-1]

    if pd.isna(latest_volume) or pd.isna(latest_volume_avg):
        print("\nNot enough data to compute volume averages.")
        return

    volume_spike = latest_volume > 1.5 * latest_volume_avg

    # Get latest prices and ATR
    latest_close = df['Close'].iloc[-1]
    latest_atr = df['ATR'].iloc[-1]

    if pd.isna(latest_atr) or pd.isna(latest_close):
        print("\nNot enough data to compute ATR or close.")
        return

    # Volatility percentage
    volatility_pct = (latest_atr / latest_close) * 100

    # Volatility Sentiment
    if volatility_pct < 5:
        sentiment = "🟢 Low volatility - good for swing trades"
    elif 5 <= volatility_pct <= 10:
        sentiment = "🟠 Moderate volatility - trade with caution"
    else:
        sentiment = "🔴 High volatility - risky trade setup"

    # Volume Sentiment
    volume_sentiment = "📈 Volume Spike Detected!" if volume_spike else "📉 Volume Normal"

    # Output
    print(f"\nLatest Close Price: ₹{latest_close:.2f}")
    print(f"Latest ATR (14): ₹{latest_atr:.2f}")
    print(f"Volatility: {volatility_pct:.2f}%")
    print(f"Volatility Sentiment: {sentiment}")
    print(f"Latest Volume: {latest_volume:,.0f}")
    print(f"20-Day Avg Volume: {latest_volume_avg:,.0f}")
    print(f"Volume Sentiment: {volume_sentiment}")

if __name__ == "__main__":
    file_path = "suzlon.csv"
    analyze_volatility_from_csv(file_path)
