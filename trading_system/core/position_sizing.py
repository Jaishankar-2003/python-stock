from config import RISK_RS

def position_size(entry_price, stop_price):
    risk_per_share = abs(entry_price - stop_price)

    if risk_per_share == 0:
        return 0

    qty = int(RISK_RS / risk_per_share)
    return max(qty, 0)
