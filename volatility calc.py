import pandas as pd

def clean_numeric_column(col):
    return pd.to_numeric(col.str.replace(',', '').str.strip(), errors='coerce')

def analyze_volatility_from_csv(file_path):
    # Load CSV
    df = pd.read_csv(file_path)

    # Standardize column names to lowercase
    df.columns = [col.strip().lower() for col in df.columns]

    # Debug: print detected columns
    print("Detected columns:", df.columns.tolist())

    # Map required columns
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

    # Validate required columns
    required = ['Open', 'High', 'Low', 'Prev Close', 'Close', 'Date']
    for req in required:
        if req not in column_map:
            print(f"Error: Couldn't detect column for '{req}'")
            return

    # Rename columns
    df = df.rename(columns={v: k for k, v in column_map.items()})

    # Convert date column
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y', errors='coerce')

    # Drop invalid dates and sort
    df = df.dropna(subset=['Date'])
    df = df.sort_values('Date').reset_index(drop=True)

    # Clean numeric values
    for col in ['Open', 'High', 'Low', 'Prev Close', 'Close']:
        df[col] = clean_numeric_column(df[col].astype(str))

    # Compute True Range
    df['TR'] = df[['High', 'Prev Close']].max(axis=1) - df[['Low', 'Prev Close']].min(axis=1)

    # Calculate ATR (14-day)
    df['ATR'] = df['TR'].rolling(window=14).mean()

    # Get latest values
    latest_atr = df['ATR'].iloc[-1]
    latest_close = df['Close'].iloc[-1]

    # Check for NaNs
    if pd.isna(latest_atr) or pd.isna(latest_close):
        print("\nNot enough data to compute ATR or closing price.")
        return

    # Volatility percentage
    volatility_pct = (latest_atr / latest_close) * 100

    # Sentiment analysis
    if volatility_pct < 5:
        sentiment = "🟢 Low volatility - good for swing trades"
    elif 5 <= volatility_pct <= 10:
        sentiment = "🟠 Moderate volatility - trade with caution"
    else:
        sentiment = "🔴 High volatility - risky trade setup"

    # Output results
    print(f"\nLatest Close Price: ₹{latest_close:.2f}")
    print(f"Latest ATR (14): ₹{latest_atr:.2f}")
    print(f"Volatility: {volatility_pct:.2f}%")
    print(f"Sentiment: {sentiment}")

if __name__ == "__main__":
    file_path = "suzlon.csv"  # Path to your CSV file
    analyze_volatility_from_csv(file_path)
