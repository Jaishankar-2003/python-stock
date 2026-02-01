def market_regime(df):
    """
    If only 1 row (snapshot) or no date column, allow market by default
    """
    if len(df) < 50 or "date" not in df.columns:
        return True   # snapshot mode

    from core.indicators import ema
    close = df["close"]
    return close.iloc[-1] > ema(close, 50).iloc[-1]


def sector_strength(df):
    """
    Snapshot-aware sector filter
    """
    if len(df) < 200 or "date" not in df.columns:
        return True   # snapshot mode

    from core.indicators import ema
    close = df["close"]
    return (
        close.iloc[-1] > ema(close, 50).iloc[-1]
        and close.iloc[-1] > ema(close, 200).iloc[-1]
    )
