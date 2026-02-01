from utils.loader import load_csv
from core.filters import market_regime, sector_strength
from core.strategies import trend_strategy, sideways_strategy
from core.backtester import backtest

def run_system(nifty_path, sector_paths, stock_paths):
    nifty = load_csv(nifty_path)
    if not market_regime(nifty):
        return {"status": "NO TRADE"}

    strong_sectors = [
        s for s, p in sector_paths.items()
        if sector_strength(load_csv(p))
    ]

    results = []
    for sector in strong_sectors:
        for stock, path in stock_paths[sector].items():
            df = load_csv(path)

            if trend_strategy(df):
                results.append({"stock": stock, "strategy": "TREND"})

            elif sideways_strategy(df):
                results.append({"stock": stock, "strategy": "SIDEWAYS"})

    return results
