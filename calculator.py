def general_trade_calculator(
        capital=None,
        entry_price=None,
        stop_loss_price=None,
        target_price=None,
        risk_perc=None,
        reward_ratio=None
):
    if not capital or not entry_price:
        return "❌ Capital and Entry Price are required."

    # Calculate risk per share
    if stop_loss_price:
        risk_per_share = entry_price - stop_loss_price
        if risk_per_share <= 0:
            return "❌ Stop-loss must be below entry price."
    elif risk_perc and capital:
        risk_amount = capital * (risk_perc / 100)
        risk_per_share = risk_amount / (capital / entry_price)
        stop_loss_price = entry_price - risk_per_share
    else:
        return "❌ Either Stop-Loss Price or Risk % is required."

    # Risk amount
    risk_amount = capital * (risk_perc / 100) if risk_perc else risk_per_share * (capital // entry_price)

    # Position size
    position_size = int(risk_amount // risk_per_share)
    invested_amount = position_size * entry_price

    # Reward/Target price
    if reward_ratio and not target_price:
        reward_per_share = risk_per_share * reward_ratio
        target_price = entry_price + reward_per_share
    elif target_price:
        reward_per_share = target_price - entry_price
        reward_ratio = reward_per_share / risk_per_share
    else:
        return "❌ Either Target Price or Reward Ratio is required."

    # Profit and % gain
    expected_profit = reward_per_share * position_size
    percent_gain = (expected_profit / capital) * 100

    return {
        "Entry Price": entry_price,
        "Stop-Loss Price": round(stop_loss_price, 2),
        "Target Price": round(target_price, 2),
        "Risk per Share": round(risk_per_share, 2),
        "Reward per Share": round(reward_per_share, 2),
        "Reward Ratio": round(reward_ratio, 2),
        "Risk Amount (₹)": round(risk_amount, 2),
        "Position Size": position_size,
        "Invested Amount (₹)": round(invested_amount, 2),
        "Expected Profit (₹)": round(expected_profit, 2),
        "Expected % Gain": round(percent_gain, 2),
    }


# -------------------------
# ✅ Sample Usage
# -------------------------
result = general_trade_calculator(
    capital=1000000,
    entry_price=800,
    stop_loss_price=790,
    reward_ratio=2,
    risk_perc=1.5,
)

if isinstance(result, dict):
    print("\n📊 Trade Plan Summary:")
    for key, value in result.items():
        print(f"{key}: {value}")
else:
    print(result)
