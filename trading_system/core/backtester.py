from core.indicators import atr
from core.position_sizing import position_size

def backtest(df, strategy_fn):
    trades = []

    for i in range(200, len(df) - 5):
        slice_df = df.iloc[:i]

        if strategy_fn(slice_df):
            entry = slice_df["close"].iloc[-1]
            stop = entry - atr(slice_df).iloc[-1]

            qty = position_size(entry, stop)
            exit_price = df["close"].iloc[i + 5]

            pnl = (exit_price - entry) * qty

            trades.append({
                "date": slice_df.index[-1],
                "entry": entry,
                "exit": exit_price,
                "qty": qty,
                "pnl": pnl
            })

    return trades
