from core.indicators import ema, rsi, atr

# TREND STRATEGY (YOUR MAIN SYSTEM)
def trend_strategy(df):
    close = df["close"]
    volume = df["volume"]

    conds = [
        close.iloc[-1] > close.rolling(20).max().shift(1).iloc[-1],
        volume.iloc[-1] > volume.rolling(20).mean().iloc[-1],
        ema(close, 20).iloc[-1] > ema(close, 50).iloc[-1],
        50 < rsi(close).iloc[-1] < 75
    ]
    return all(conds)

# SIDEWAYS STRATEGY (RANGE BREAK + MEAN REVERT)
def sideways_strategy(df):
    r = rsi(df["close"])
    return r.iloc[-1] < 30 or r.iloc[-1] > 70
