# import pandas as pd
# import numpy as np
# import glob
#
# import row
#
# # =========================================================
# # CONFIG
# # =========================================================
#
# LOOKBACK = 20
# RSI_PERIOD = 14
#
# TARGET_PCT = 0.05
# STOP_PCT = 0.02
#
# STRICTNESS = 0.90
#
# REQUIRED_COLUMNS = {"OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"}
#
#
# # =========================================================
# # DATA CLEANING
# # =========================================================
#
# def clean_numeric_columns(df):
#     numeric_cols = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
#
#     for col in numeric_cols:
#         if col in df.columns:
#             df[col] = (
#                 df[col]
#                 .astype(str)
#                 .str.replace(",", "", regex=False)
#                 .str.replace("₹", "", regex=False)
#                 .str.strip()
#             )
#             df[col] = pd.to_numeric(df[col], errors="coerce")
#
#     return df
#
#
# def detect_date_column(df):
#     possible = ["DATE", "Date", "TIMESTAMP", "Timestamp", "date", "timestamp"]
#     for c in possible:
#         if c in df.columns:
#             return c
#     return None
#
#
# def load_csv(csv_file):
#     df = pd.read_csv(csv_file)
#
#     df.columns = [c.strip() for c in df.columns]
#
#     date_col = detect_date_column(df)
#
#     if date_col:
#         df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
#         df = df.dropna(subset=[date_col])
#         df = df.sort_values(date_col).reset_index(drop=True)
#     else:
#         print("⚠️ WARNING: No DATE column found. Indicators may be wrong if CSV is reversed.")
#
#     df = clean_numeric_columns(df)
#
#     missing = REQUIRED_COLUMNS - set(df.columns)
#     if missing:
#         raise ValueError(f"Missing required columns: {missing}")
#
#     df = df.dropna(subset=["CLOSE", "HIGH", "LOW", "OPEN", "VOLUME"]).reset_index(drop=True)
#
#     return df
#
#
# # =========================================================
# # INDICATORS
# # =========================================================
#
# def ema(series, span):
#     return series.ewm(span=span, adjust=False).mean()
#
#
# def rsi_wilder(series, period=RSI_PERIOD):
#     delta = series.diff()
#
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)
#
#     avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
#     avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
#
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#
#     rsi = rsi.where(avg_loss != 0, 100)
#     rsi = rsi.where(avg_gain != 0, 0)
#
#     return rsi
#
#
# def rsi_sma(series, period=RSI_PERIOD):
#     delta = series.diff()
#
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)
#
#     avg_gain = gain.rolling(period).mean()
#     avg_loss = loss.rolling(period).mean()
#
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#
#     rsi = rsi.where(avg_loss != 0, 100)
#     rsi = rsi.where(avg_gain != 0, 0)
#
#     return rsi
#
#
# def add_indicators(df):
#     df = df.copy()
#
#     df["EMA20"] = ema(df["CLOSE"], 20)
#     df["EMA50"] = ema(df["CLOSE"], 50)
#     df["EMA200"] = ema(df["CLOSE"], 200)
#
#     df["RSI_WILDER"] = rsi_wilder(df["CLOSE"], RSI_PERIOD)
#     df["RSI_SMA"] = rsi_sma(df["CLOSE"], RSI_PERIOD)
#
#     df["AvgVol20"] = df["VOLUME"].rolling(20).mean()
#
#     return df
#
#
# # =========================================================
# # STRICTNESS / SCORING SYSTEM
# # =========================================================
#
# def strictness_required_score(strictness: float) -> int:
#     if strictness >= 0.95:
#         return 4
#     return 3
#
#
# def get_liberal_params(strictness: float):
#     if strictness >= 0.95:
#         return {
#             "vol_multiplier": 1.5,
#             "rsi_low": 50,
#             "rsi_high": 75,
#             "near_breakout_pct": 0.99,
#         }
#
#     if strictness >= 0.90:
#         return {
#             "vol_multiplier": 1.2,
#             "rsi_low": 48,
#             "rsi_high": 78,
#             "near_breakout_pct": 0.985,
#         }
#
#     return {
#         "vol_multiplier": 1.0,
#         "rsi_low": 45,
#         "rsi_high": 80,
#         "near_breakout_pct": 0.98,
#     }
#
#
# # =========================================================
# # STRATEGY LOGIC
# # =========================================================
#
# def evaluate_conditions(row, prev_high, params):
#     breakout = row["CLOSE"] > prev_high
#     near_breakout = row["CLOSE"] > prev_high * params["near_breakout_pct"]
#
#     vol_ok = row["VOLUME"] > params["vol_multiplier"] * row["AvgVol20"]
#     trend_ok = row["CLOSE"] > row["EMA20"] > row["EMA50"]
#
#     rsi_val = row["RSI_WILDER"]
#     rsi_ok = params["rsi_low"] <= rsi_val <= params["rsi_high"]
#
#     return breakout, near_breakout, vol_ok, trend_ok, rsi_ok
#
#
# # =========================================================
# # ENTRY RULE (STRICT + LITE LIBERAL)
# # =========================================================
#
# def should_buy_signal(breakout, near_breakout, vol_ok, trend_ok, rsi_ok, score, required):
#     # strict breakout rule (unchanged)
#     if breakout and score >= required and row["CLOSE"] > row["EMA200"]:
#         return True, "STRICT_BREAKOUT"
#
#     # ✅ lite liberal rule
#     if near_breakout and trend_ok and (vol_ok or rsi_ok):
#         return True, "LITE_NEAR_BREAKOUT"
#
#     return False, None
#
#
# # =========================================================
# # SIGNAL
# # =========================================================
#
# def technical_signal(df, lookback=LOOKBACK, strictness=STRICTNESS):
#     df = add_indicators(df)
#     last = df.iloc[-1]
#
#     if pd.isna(last["RSI_WILDER"]) or pd.isna(last["EMA50"]) or pd.isna(last["AvgVol20"]):
#         return "NO TRADE"
#
#     params = get_liberal_params(strictness)
#     required = strictness_required_score(strictness)
#
#     prev_high = df["HIGH"].iloc[-lookback-1:-1].max()
#
#     breakout, near_breakout, vol_ok, trend_ok, rsi_ok = evaluate_conditions(last, prev_high, params)
#
#     conditions = [breakout, vol_ok, trend_ok, rsi_ok]
#     score = sum(bool(x) for x in conditions)
#
#     buy, _ = should_buy_signal(breakout, near_breakout, vol_ok, trend_ok, rsi_ok, score, required)
#
#     if buy:
#         return "BUY TRIGGER"
#
#     if near_breakout and trend_ok:
#         return "PREPARE"
#
#     return "NO TRADE"
#
#
# # =========================================================
# # DEBUG
# # =========================================================
#
# def debug_conditions(df, lookback=LOOKBACK, strictness=STRICTNESS):
#     df = add_indicators(df)
#     last = df.iloc[-1]
#
#     if pd.isna(last["RSI_WILDER"]):
#         print("\n🔍 CONDITION CHECK (LAST CANDLE)")
#         print("RSI not ready – insufficient data")
#         return
#
#     params = get_liberal_params(strictness)
#     required = strictness_required_score(strictness)
#
#     prev_high = df["HIGH"].iloc[-lookback-1:-1].max()
#
#     breakout, near_breakout, vol_ok, trend_ok, rsi_ok = evaluate_conditions(last, prev_high, params)
#
#     conditions = [breakout, vol_ok, trend_ok, rsi_ok]
#     score = sum(bool(x) for x in conditions)
#
#     buy, reason = should_buy_signal(breakout, near_breakout, vol_ok, trend_ok, rsi_ok, score, required)
#
#     print("\n🔍 CONDITION CHECK (LAST CANDLE)")
#     print("Strictness Mode:", strictness)
#     print("Breakout:", breakout)
#     print("Near Breakout:", near_breakout)
#     print("Volume Spike:", vol_ok)
#     print("Trend OK:", trend_ok)
#     print("RSI OK:", rsi_ok)
#     print("BUY Logic:", buy, "| Reason:", reason)
#
#     print("\n📌 RSI VALUES (SIDE BY SIDE)")
#     print("RSI_WILDER:", round(last["RSI_WILDER"], 2))
#     print("RSI_SMA   :", round(last["RSI_SMA"], 2))
#
#     print("\n📌 EXTRA INFO")
#     print("Close:", last["CLOSE"])
#     print("Prev 20D High:", prev_high)
#     print("AvgVol20:", round(last["AvgVol20"], 2))
#     print("Volume:", last["VOLUME"])
#
#     if not pd.isna(last["EMA200"]):
#         print("EMA200:", round(last["EMA200"], 2))
#
#
# # =========================================================
# # EXPORT
# # =========================================================
#
# def export_signal(df, signal, source_file):
#     df = add_indicators(df)
#     last = df.iloc[-1]
#
#     out = pd.DataFrame([{
#         "Stock": source_file.split("/")[-1],
#         "Close": last["CLOSE"],
#         "Volume": last["VOLUME"],
#         "Signal": signal,
#         "RSI_WILDER": round(last["RSI_WILDER"], 2),
#         "RSI_SMA": round(last["RSI_SMA"], 2),
#         "EMA20": round(last["EMA20"], 2),
#         "EMA50": round(last["EMA50"], 2),
#         "EMA200": round(last["EMA200"], 2),
#     }])
#
#     out.to_csv(
#         "trade_signals.csv",
#         mode="a",
#         header=not pd.io.common.file_exists("trade_signals.csv"),
#         index=False
#     )
#
#     print("✔ Signal exported")
#
#
# # =========================================================
# # BACKTEST (REALISTIC + LITE LIBERAL ENTRY)
# # =========================================================
#
# def backtest_strategy(df, lookback=LOOKBACK,
#                       target_pct=TARGET_PCT,
#                       stop_pct=STOP_PCT,
#                       strictness=STRICTNESS):
#
#     df = add_indicators(df)
#     df = df.reset_index(drop=True)
#
#     params = get_liberal_params(strictness)
#     required = strictness_required_score(strictness)
#
#     trades = []
#     in_trade = False
#
#     entry_price = None
#     entry_date = None
#     target = None
#     stop = None
#     entry_reason = None
#
#     date_col = detect_date_column(df)
#
#     start_i = max(lookback + 1, 220)
#
#     for i in range(start_i, len(df) - 2):
#         row = df.iloc[i]
#
#         if pd.isna(row["RSI_WILDER"]) or pd.isna(row["EMA50"]) or pd.isna(row["AvgVol20"]):
#             continue
#
#         # ENTRY
#         if not in_trade:
#             prev_high = df["HIGH"].iloc[i-lookback:i].max()
#
#             breakout, near_breakout, vol_ok, trend_ok, rsi_ok = evaluate_conditions(row, prev_high, params)
#
#             conditions = [breakout, vol_ok, trend_ok, rsi_ok]
#             score = sum(bool(x) for x in conditions)
#
#             buy, reason = should_buy_signal(breakout, near_breakout, vol_ok, trend_ok, rsi_ok, score, required)
#
#             if buy:
#                 next_day = df.iloc[i + 1]
#                 entry_price = next_day["OPEN"]
#
#                 if pd.isna(entry_price):
#                     continue
#
#                 entry_date = next_day[date_col] if date_col else (i + 1)
#                 entry_reason = reason
#
#                 target = entry_price * (1 + target_pct)
#                 stop = entry_price * (1 - stop_pct)
#
#                 in_trade = True
#                 continue
#
#         # EXIT
#         else:
#             candle = df.iloc[i]
#             open_ = candle["OPEN"]
#             high = candle["HIGH"]
#             low = candle["LOW"]
#
#             exit_price = None
#             exit_reason = None
#             result = None
#
#             if open_ >= target:
#                 exit_price = open_
#                 result = "WIN"
#                 exit_reason = "GAP_TARGET"
#
#             elif open_ <= stop:
#                 exit_price = open_
#                 result = "LOSS"
#                 exit_reason = "GAP_STOP"
#
#             else:
#                 hit_target = high >= target
#                 hit_stop = low <= stop
#
#                 if hit_stop and hit_target:
#                     exit_price = stop
#                     result = "LOSS"
#                     exit_reason = "BOTH_HIT_ASSUME_STOP"
#
#                 elif hit_target:
#                     exit_price = target
#                     result = "WIN"
#                     exit_reason = "TARGET_HIT"
#
#                 elif hit_stop:
#                     exit_price = stop
#                     result = "LOSS"
#                     exit_reason = "STOP_HIT"
#
#                 else:
#                     continue
#
#             exit_date = candle[date_col] if date_col else i
#             ret_pct = ((exit_price - entry_price) / entry_price) * 100
#
#             trades.append({
#                 "EntryDate": entry_date,
#                 "EntryPrice": round(entry_price, 2),
#                 "EntryReason": entry_reason,
#                 "ExitDate": exit_date,
#                 "ExitPrice": round(exit_price, 2),
#                 "Result": result,
#                 "ReturnPct": round(ret_pct, 2),
#                 "ExitReason": exit_reason,
#             })
#
#             in_trade = False
#             entry_price = None
#             entry_date = None
#             target = None
#             stop = None
#             entry_reason = None
#
#     if not trades:
#         print("No trades found in backtest")
#         return
#
#     results_df = pd.DataFrame(trades)
#
#     wins = (results_df["Result"] == "WIN").sum()
#     total = len(results_df)
#     win_rate = wins / total * 100
#
#     print("\n📊 BACKTEST RESULT")
#     print("Strictness Mode:", strictness)
#     print("Total Trades:", total)
#     print("Winning Trades:", wins)
#     print("Win Rate:", round(win_rate, 2), "%")
#
#     results_df.to_csv("backtest_trades.csv", index=False)
#     print("✔ Trade log exported: backtest_trades.csv")
#
#
# # =========================================================
# # MAIN
# # =========================================================
#
# if __name__ == "__main__":
#     csv_paths = glob.glob("csv file/*.csv")
#
#     for csv_path in csv_paths:
#         print(f"\nProcessing: {csv_path}")
#
#         df = load_csv(csv_path)
#         debug_conditions(df)
#
#         signal = technical_signal(df)
#         print("Signal:", signal)
#         print("==================================================================")
#         export_signal(df, signal, csv_path)
#         backtest_strategy(df)
#
#
#======================================================================================================================================================================

# import pandas as pd
# import numpy as np
# import glob
#
# # =========================================================
# # CONFIG
# # =========================================================
#
# LOOKBACK = 20
# RSI_PERIOD = 14
#
# TARGET_PCT = 0.05
# STOP_PCT = 0.02
#
# STRICTNESS = 0.90
#
# REQUIRED_COLUMNS = {"OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"}
#
#
# # =========================================================
# # DATA CLEANING
# # =========================================================
#
# def clean_numeric_columns(df):
#     numeric_cols = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
#
#     for col in numeric_cols:
#         if col in df.columns:
#             df[col] = (
#                 df[col]
#                 .astype(str)
#                 .str.replace(",", "", regex=False)
#                 .str.replace("₹", "", regex=False)
#                 .str.strip()
#             )
#             df[col] = pd.to_numeric(df[col], errors="coerce")
#
#     return df
#
#
# def detect_date_column(df):
#     possible = ["DATE", "Date", "TIMESTAMP", "Timestamp", "date", "timestamp"]
#     for c in possible:
#         if c in df.columns:
#             return c
#     return None
#
#
# def load_csv(csv_file):
#     df = pd.read_csv(csv_file)
#     df.columns = [c.strip() for c in df.columns]
#
#     date_col = detect_date_column(df)
#
#     if date_col:
#         df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
#         df = df.dropna(subset=[date_col])
#         df = df.sort_values(date_col).reset_index(drop=True)
#     else:
#         print("⚠️ WARNING: No DATE column found. Indicators may be wrong if CSV is reversed.")
#
#     df = clean_numeric_columns(df)
#
#     missing = REQUIRED_COLUMNS - set(df.columns)
#     if missing:
#         raise ValueError(f"Missing required columns: {missing}")
#
#     df = df.dropna(subset=["CLOSE", "HIGH", "LOW", "OPEN", "VOLUME"]).reset_index(drop=True)
#
#     return df
#
#
# # =========================================================
# # INDICATORS
# # =========================================================
#
# def ema(series, span):
#     return series.ewm(span=span, adjust=False).mean()
#
#
# def rsi_wilder(series, period=RSI_PERIOD):
#     delta = series.diff()
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)
#
#     avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
#     avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
#
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#
#     rsi = rsi.where(avg_loss != 0, 100)
#     rsi = rsi.where(avg_gain != 0, 0)
#
#     return rsi
#
#
# def rsi_sma(series, period=RSI_PERIOD):
#     delta = series.diff()
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)
#
#     avg_gain = gain.rolling(period).mean()
#     avg_loss = loss.rolling(period).mean()
#
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#
#     rsi = rsi.where(avg_loss != 0, 100)
#     rsi = rsi.where(avg_gain != 0, 0)
#
#     return rsi
#
#
# def add_indicators(df):
#     df = df.copy()
#
#     df["EMA20"] = ema(df["CLOSE"], 20)
#     df["EMA50"] = ema(df["CLOSE"], 50)
#     df["EMA200"] = ema(df["CLOSE"], 200)
#
#     df["RSI_WILDER"] = rsi_wilder(df["CLOSE"], RSI_PERIOD)
#     df["RSI_SMA"] = rsi_sma(df["CLOSE"], RSI_PERIOD)
#
#     df["AvgVol20"] = df["VOLUME"].rolling(20).mean()
#
#     return df
#
#
# # =========================================================
# # STRICTNESS / SCORING SYSTEM
# # =========================================================
#
# def strictness_required_score(strictness: float) -> int:
#     return 4 if strictness >= 0.95 else 3
#
#
# def get_liberal_params(strictness: float):
#     if strictness >= 0.95:
#         return {
#             "vol_multiplier": 1.5,
#             "rsi_low": 50,
#             "rsi_high": 75,
#             "near_breakout_pct": 0.99,
#         }
#
#     if strictness >= 0.90:
#         return {
#             "vol_multiplier": 1.2,
#             "rsi_low": 48,
#             "rsi_high": 78,
#             "near_breakout_pct": 0.985,
#         }
#
#     return {
#         "vol_multiplier": 1.0,
#         "rsi_low": 45,
#         "rsi_high": 80,
#         "near_breakout_pct": 0.98,
#     }
#
#
# # =========================================================
# # STRATEGY LOGIC
# # =========================================================
#
# def evaluate_conditions(row, prev_high, params):
#     breakout = row["CLOSE"] > prev_high
#     near_breakout = row["CLOSE"] > prev_high * params["near_breakout_pct"]
#
#     vol_ok = row["VOLUME"] > params["vol_multiplier"] * row["AvgVol20"]
#
#     # Swing trend logic (improved)
#     trend_ok = (row["EMA20"] > row["EMA50"]) and (row["CLOSE"] > row["EMA50"])
#     ema200_ok = row["CLOSE"] > row["EMA200"]
#
#     rsi_val = row["RSI_WILDER"]
#     rsi_ok = params["rsi_low"] <= rsi_val <= params["rsi_high"]
#
#     return breakout, near_breakout, vol_ok, trend_ok, ema200_ok, rsi_ok
#
#
# # =========================================================
# # ENTRY RULES
# # =========================================================
#
# def should_buy_signal(breakout, near_breakout, vol_ok, trend_ok, ema200_ok, rsi_ok, score, required):
#
#     # STRICT BREAKOUT = only above EMA200
#     if breakout and ema200_ok and score >= required:
#         return True, "STRICT_BREAKOUT_EMA200"
#
#     # LITE breakout = allow above EMA50 trend
#     if breakout and trend_ok and vol_ok and rsi_ok:
#         return True, "BREAKOUT_EMA50"
#
#     # Near breakout entry
#     if near_breakout and trend_ok and (vol_ok or rsi_ok):
#         return True, "LITE_NEAR_BREAKOUT"
#
#     return False, None
#
#
# # =========================================================
# # SIGNAL
# # =========================================================
#
# def technical_signal(df, lookback=LOOKBACK, strictness=STRICTNESS):
#     df = add_indicators(df)
#     last = df.iloc[-1]
#
#     if pd.isna(last["RSI_WILDER"]) or pd.isna(last["EMA50"]) or pd.isna(last["AvgVol20"]):
#         return "NO TRADE"
#
#     params = get_liberal_params(strictness)
#     required = strictness_required_score(strictness)
#
#     prev_high = df["HIGH"].iloc[-lookback-1:-1].max()
#
#     breakout, near_breakout, vol_ok, trend_ok, ema200_ok, rsi_ok = evaluate_conditions(last, prev_high, params)
#
#     conditions = [breakout, vol_ok, trend_ok, rsi_ok]
#     score = sum(bool(x) for x in conditions)
#
#     buy, _ = should_buy_signal(breakout, near_breakout, vol_ok, trend_ok, ema200_ok, rsi_ok, score, required)
#
#     if buy:
#         return "BUY TRIGGER"
#
#     if near_breakout and trend_ok:
#         return "PREPARE"
#
#     return "NO TRADE"
#
#
# # =========================================================
# # DEBUG
# # =========================================================
#
# def debug_conditions(df, lookback=LOOKBACK, strictness=STRICTNESS):
#     df = add_indicators(df)
#     last = df.iloc[-1]
#
#     if pd.isna(last["RSI_WILDER"]):
#         print("\n🔍 CONDITION CHECK (LAST CANDLE)")
#         print("RSI not ready – insufficient data")
#         return
#
#     params = get_liberal_params(strictness)
#     required = strictness_required_score(strictness)
#
#     prev_high = df["HIGH"].iloc[-lookback-1:-1].max()
#
#     breakout, near_breakout, vol_ok, trend_ok, ema200_ok, rsi_ok = evaluate_conditions(last, prev_high, params)
#
#     conditions = [breakout, vol_ok, trend_ok, rsi_ok]
#     score = sum(bool(x) for x in conditions)
#
#     buy, reason = should_buy_signal(breakout, near_breakout, vol_ok, trend_ok, ema200_ok, rsi_ok, score, required)
#
#     print("\n🔍 CONDITION CHECK (LAST CANDLE)")
#     print("Strictness Mode:", strictness)
#     print("Breakout:", breakout)
#     print("Near Breakout:", near_breakout)
#     print("Volume Spike:", vol_ok)
#     print("Trend OK:", trend_ok)
#     print("Above EMA200:", ema200_ok)
#     print("RSI OK:", rsi_ok)
#     print("BUY Logic:", buy, "| Reason:", reason)
#
#     print("\n📌 EXTRA INFO")
#     print("Close:", last["CLOSE"])
#     print("Prev 20D High:", prev_high)
#     print("AvgVol20:", round(last["AvgVol20"], 2))
#     print("Volume:", last["VOLUME"])
#     print("EMA20:", round(last["EMA20"], 2))
#     print("EMA50:", round(last["EMA50"], 2))
#     print("EMA200:", round(last["EMA200"], 2))
#
#
# # =========================================================
# # MAIN
# # =========================================================
#
# if __name__ == "__main__":
#     csv_paths = glob.glob("csv file/*.csv")
#
#     for csv_path in csv_paths:
#         print(f"\nProcessing: {csv_path}")
#
#         df = load_csv(csv_path)
#
#         debug_conditions(df)
#         signal = technical_signal(df)
#
#         print("Signal:", signal)
#         print("==================================================================")

#=====================================================================================================================================================================================

# import pandas as pd
# import numpy as np
# import glob
#
# # =========================================================
# # CONFIG
# # =========================================================
#
# LOOKBACK = 20
# RSI_PERIOD = 14
#
# TARGET_PCT = 0.05
# STOP_PCT = 0.02
#
# STRICTNESS = 0.90
#
# REQUIRED_COLUMNS = {"OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"}
#
#
# # =========================================================
# # DATA CLEANING
# # =========================================================
#
# def clean_numeric_columns(df):
#     numeric_cols = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
#
#     for col in numeric_cols:
#         if col in df.columns:
#             df[col] = (
#                 df[col]
#                 .astype(str)
#                 .str.replace(",", "", regex=False)
#                 .str.replace("₹", "", regex=False)
#                 .str.strip()
#             )
#             df[col] = pd.to_numeric(df[col], errors="coerce")
#
#     return df
#
#
# def detect_date_column(df):
#     possible = ["DATE", "Date", "TIMESTAMP", "Timestamp", "date", "timestamp"]
#     for c in possible:
#         if c in df.columns:
#             return c
#     return None
#
#
# def load_csv(csv_file):
#     df = pd.read_csv(csv_file)
#     df.columns = [c.strip() for c in df.columns]
#
#     date_col = detect_date_column(df)
#
#     if date_col:
#         df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
#         df = df.dropna(subset=[date_col])
#         df = df.sort_values(date_col).reset_index(drop=True)
#     else:
#         print("⚠️ WARNING: No DATE column found. Indicators may be wrong if CSV is reversed.")
#
#     df = clean_numeric_columns(df)
#
#     missing = REQUIRED_COLUMNS - set(df.columns)
#     if missing:
#         raise ValueError(f"Missing required columns: {missing}")
#
#     df = df.dropna(subset=["CLOSE", "HIGH", "LOW", "OPEN", "VOLUME"]).reset_index(drop=True)
#
#     return df
#
#
# # =========================================================
# # INDICATORS
# # =========================================================
#
# def ema(series, span):
#     return series.ewm(span=span, adjust=False).mean()
#
#
# def rsi_wilder(series, period=RSI_PERIOD):
#     delta = series.diff()
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)
#
#     avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
#     avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
#
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#
#     rsi = rsi.where(avg_loss != 0, 100)
#     rsi = rsi.where(avg_gain != 0, 0)
#
#     return rsi
#
#
# def rsi_sma(series, period=RSI_PERIOD):
#     delta = series.diff()
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)
#
#     avg_gain = gain.rolling(period).mean()
#     avg_loss = loss.rolling(period).mean()
#
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#
#     rsi = rsi.where(avg_loss != 0, 100)
#     rsi = rsi.where(avg_gain != 0, 0)
#
#     return rsi
#
#
# def add_indicators(df):
#     df = df.copy()
#
#     df["EMA20"] = ema(df["CLOSE"], 20)
#     df["EMA50"] = ema(df["CLOSE"], 50)
#     df["EMA200"] = ema(df["CLOSE"], 200)
#
#     df["RSI_WILDER"] = rsi_wilder(df["CLOSE"], RSI_PERIOD)
#     df["RSI_SMA"] = rsi_sma(df["CLOSE"], RSI_PERIOD)
#
#     df["AvgVol20"] = df["VOLUME"].rolling(20).mean()
#
#     return df
#
#
# # =========================================================
# # STRICTNESS / SCORING SYSTEM
# # =========================================================
#
# def strictness_required_score(strictness: float) -> int:
#     return 4 if strictness >= 0.95 else 3
#
#
# def get_liberal_params(strictness: float):
#     if strictness >= 0.95:
#         return {
#             "vol_multiplier": 1.5,
#             "rsi_low": 50,
#             "rsi_high": 75,
#             "near_breakout_pct": 0.99,
#         }
#
#     if strictness >= 0.90:
#         return {
#             "vol_multiplier": 1.2,
#             "rsi_low": 48,
#             "rsi_high": 78,
#             "near_breakout_pct": 0.985,
#         }
#
#     return {
#         "vol_multiplier": 1.0,
#         "rsi_low": 45,
#         "rsi_high": 80,
#         "near_breakout_pct": 0.98,
#     }
#
#
# # =========================================================
# # STRATEGY LOGIC
# # =========================================================
#
# def evaluate_conditions(row, prev_high, params):
#     breakout = row["CLOSE"] > prev_high
#     near_breakout = row["CLOSE"] > prev_high * params["near_breakout_pct"]
#
#     vol_ok = row["VOLUME"] > params["vol_multiplier"] * row["AvgVol20"]
#
#     # EARLY TREND (EMA50 based)
#     early_trend_ok = (row["EMA20"] > row["EMA50"]) and (row["CLOSE"] > row["EMA50"])
#
#     # CONFIRM TREND (EMA200 based)
#     ema200_ok = row["CLOSE"] > row["EMA200"]
#
#     rsi_val = row["RSI_WILDER"]
#     rsi_ok = params["rsi_low"] <= rsi_val <= params["rsi_high"]
#
#     return breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok
#
#
# # =========================================================
# # ENTRY RULES (2 STAGE)
# # =========================================================
#
# def should_buy_signal(breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok, score, required):
#
#     # 🟩 STAGE-2 CONFIRM BUY (only above EMA200)
#     if breakout and ema200_ok and score >= required:
#         return True, "CONFIRM_BUY_EMA200"
#
#     # 🟢 STAGE-1 EARLY BUY (below EMA200 allowed)
#     if breakout and early_trend_ok and vol_ok and rsi_ok:
#         return True, "EARLY_BUY_EMA50"
#
#     # 🟡 PREPARE (near breakout but not confirmed)
#     if near_breakout and early_trend_ok and (vol_ok or rsi_ok):
#         return True, "PREPARE"
#
#     return False, None
#
#
# # =========================================================
# # SIGNAL
# # =========================================================
#
# def technical_signal(df, lookback=LOOKBACK, strictness=STRICTNESS):
#     df = add_indicators(df)
#     last = df.iloc[-1]
#
#     if pd.isna(last["RSI_WILDER"]) or pd.isna(last["EMA50"]) or pd.isna(last["AvgVol20"]):
#         return "NO_TRADE"
#
#     params = get_liberal_params(strictness)
#     required = strictness_required_score(strictness)
#
#     prev_high = df["HIGH"].iloc[-lookback-1:-1].max()
#
#     breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok = evaluate_conditions(
#         last, prev_high, params
#     )
#
#     conditions = [breakout, vol_ok, early_trend_ok, rsi_ok]
#     score = sum(bool(x) for x in conditions)
#
#     buy, reason = should_buy_signal(
#         breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok, score, required
#     )
#
#     if not buy:
#         return "NO_TRADE"
#
#     # Return proper stage
#     if reason == "CONFIRM_BUY_EMA200":
#         return "CONFIRM_BUY"
#
#     if reason == "EARLY_BUY_EMA50":
#         return "EARLY_BUY"
#
#     if reason == "PREPARE":
#         return "PREPARE"
#
#     return "NO_TRADE"
#
#
# # =========================================================
# # DEBUG
# # =========================================================
#
# def debug_conditions(df, lookback=LOOKBACK, strictness=STRICTNESS):
#     df = add_indicators(df)
#     last = df.iloc[-1]
#
#     if pd.isna(last["RSI_WILDER"]):
#         print("\n🔍 CONDITION CHECK (LAST CANDLE)")
#         print("RSI not ready – insufficient data")
#         return
#
#     params = get_liberal_params(strictness)
#     required = strictness_required_score(strictness)
#
#     prev_high = df["HIGH"].iloc[-lookback-1:-1].max()
#
#     breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok = evaluate_conditions(
#         last, prev_high, params
#     )
#
#     conditions = [breakout, vol_ok, early_trend_ok, rsi_ok]
#     score = sum(bool(x) for x in conditions)
#
#     buy, reason = should_buy_signal(
#         breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok, score, required
#     )
#
#     print("\n🔍 CONDITION CHECK (LAST CANDLE)")
#     print("Strictness Mode:", strictness)
#     print("Breakout:", breakout)
#     print("Near Breakout:", near_breakout)
#     print("Volume Spike:", vol_ok)
#     print("Early Trend OK (EMA50):", early_trend_ok)
#     print("Above EMA200:", ema200_ok)
#     print("RSI OK:", rsi_ok)
#     print("BUY Logic:", buy, "| Reason:", reason)
#
#     print("\n📌 EXTRA INFO")
#     print("Close:", last["CLOSE"])
#     print("Prev 20D High:", prev_high)
#     print("AvgVol20:", round(last["AvgVol20"], 2))
#     print("Volume:", last["VOLUME"])
#     print("EMA20:", round(last["EMA20"], 2))
#     print("EMA50:", round(last["EMA50"], 2))
#     print("EMA200:", round(last["EMA200"], 2))
#
#
# # =========================================================
# # MAIN
# # =========================================================
#
# if __name__ == "__main__":
#     csv_paths = glob.glob("csv file/*.csv")
#
#     for csv_path in csv_paths:
#         print(f"\nProcessing: {csv_path}")
#
#         df = load_csv(csv_path)
#
#         debug_conditions(df)
#         signal = technical_signal(df)
#
#         print("Signal:", signal)
#         print("==================================================================")
#
#


#===================================================================================================================== revision  5 ========================================================


import pandas as pd
import numpy as np
import glob

# =========================================================
# CONFIG
# =========================================================

LOOKBACK = 20
RSI_PERIOD = 14
ATR_PERIOD = 14

TARGET_PCT = 0.05
STOP_PCT = 0.02

STRICTNESS = 0.90

REQUIRED_COLUMNS = {"OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"}

# ✅ NEW FILTERS (SAFE)
BREAKOUT_CONFIRM_PCT = 1.003
CLOSE_STRENGTH_LEVEL = 0.70
RETEST_ZONE_PCT = 0.015
TWO_DAY_CONFIRM_NEAR = 0.995

# ✅ ATR STOP SETTINGS (SAFE)
ATR_MULT_EARLY = 2.0
ATR_MULT_CONFIRM = 1.5
ATR_MULT_RETEST = 1.8


# =========================================================
# DATA CLEANING
# =========================================================

def clean_numeric_columns(df):
    numeric_cols = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("₹", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def detect_date_column(df):
    possible = ["DATE", "Date", "TIMESTAMP", "Timestamp", "date", "timestamp"]
    for c in possible:
        if c in df.columns:
            return c
    return None


def load_csv(csv_file):
    df = pd.read_csv(csv_file)
    df.columns = [c.strip() for c in df.columns]

    date_col = detect_date_column(df)

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
        df = df.dropna(subset=[date_col])
        df = df.sort_values(date_col).reset_index(drop=True)
    else:
        print("⚠️ WARNING: No DATE column found. Indicators may be wrong if CSV is reversed.")

    df = clean_numeric_columns(df)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.dropna(subset=["CLOSE", "HIGH", "LOW", "OPEN", "VOLUME"]).reset_index(drop=True)

    return df


# =========================================================
# INDICATORS
# =========================================================

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def rsi_wilder(series, period=RSI_PERIOD):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.where(avg_loss != 0, 100)
    rsi = rsi.where(avg_gain != 0, 0)

    return rsi


def rsi_sma(series, period=RSI_PERIOD):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.where(avg_loss != 0, 100)
    rsi = rsi.where(avg_gain != 0, 0)

    return rsi


def atr(df, period=ATR_PERIOD):
    """
    ATR using Wilder smoothing.
    """
    high = df["HIGH"]
    low = df["LOW"]
    close = df["CLOSE"]

    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr_val = true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    return atr_val


def add_indicators(df):
    df = df.copy()

    df["EMA20"] = ema(df["CLOSE"], 20)
    df["EMA50"] = ema(df["CLOSE"], 50)
    df["EMA200"] = ema(df["CLOSE"], 200)

    df["RSI_WILDER"] = rsi_wilder(df["CLOSE"], RSI_PERIOD)
    df["RSI_SMA"] = rsi_sma(df["CLOSE"], RSI_PERIOD)

    df["AvgVol20"] = df["VOLUME"].rolling(20).mean()

    # ✅ ATR
    df["ATR14"] = atr(df, ATR_PERIOD)

    return df


# =========================================================
# STRICTNESS / SCORING SYSTEM
# =========================================================

def strictness_required_score(strictness: float) -> int:
    return 4 if strictness >= 0.95 else 3


def get_liberal_params(strictness: float):
    if strictness >= 0.95:
        return {
            "vol_multiplier": 1.5,
            "rsi_low": 50,
            "rsi_high": 75,
            "near_breakout_pct": 0.99,
        }

    if strictness >= 0.90:
        return {
            "vol_multiplier": 1.2,
            "rsi_low": 48,
            "rsi_high": 78,
            "near_breakout_pct": 0.985,
        }

    return {
        "vol_multiplier": 1.0,
        "rsi_low": 45,
        "rsi_high": 80,
        "near_breakout_pct": 0.98,
    }


# =========================================================
# STRATEGY LOGIC
# =========================================================

def evaluate_conditions(row, prev_high, params):
    breakout = row["CLOSE"] > prev_high * BREAKOUT_CONFIRM_PCT
    near_breakout = row["CLOSE"] > prev_high * params["near_breakout_pct"]

    vol_ok = row["VOLUME"] > params["vol_multiplier"] * row["AvgVol20"]

    early_trend_ok = (row["EMA20"] > row["EMA50"]) and (row["CLOSE"] > row["EMA50"])
    ema200_ok = row["CLOSE"] > row["EMA200"]

    rsi_val = row["RSI_WILDER"]
    rsi_ok = params["rsi_low"] <= rsi_val <= params["rsi_high"]

    candle_range = row["HIGH"] - row["LOW"]
    if candle_range <= 0:
        close_strong = False
    else:
        close_strong = row["CLOSE"] > (row["LOW"] + CLOSE_STRENGTH_LEVEL * candle_range)

    near_ema20 = abs(row["CLOSE"] - row["EMA20"]) / row["EMA20"] <= RETEST_ZONE_PCT
    near_ema50 = abs(row["CLOSE"] - row["EMA50"]) / row["EMA50"] <= RETEST_ZONE_PCT
    retest_zone = near_ema20 or near_ema50

    return breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok, close_strong, retest_zone


# =========================================================
# 2-DAY BREAKOUT CONFIRMATION (ONLY FOR CONFIRM_BUY)
# =========================================================

def two_day_breakout_confirm(df, lookback=LOOKBACK):
    if len(df) < lookback + 3:
        return False

    today = df.iloc[-1]
    yesterday = df.iloc[-2]

    prev_high = df["HIGH"].iloc[-lookback-2:-2].max()

    today_breakout = today["CLOSE"] > prev_high * BREAKOUT_CONFIRM_PCT
    yesterday_near = yesterday["CLOSE"] > prev_high * TWO_DAY_CONFIRM_NEAR

    return bool(today_breakout and yesterday_near)


# =========================================================
# ENTRY RULES
# =========================================================

def should_buy_signal(
    breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok,
    rsi_ok, close_strong, retest_zone,
    score, required,
    confirm_2day
):

    if breakout and ema200_ok and score >= required and close_strong and confirm_2day:
        return True, "CONFIRM_BUY_EMA200"

    if breakout and early_trend_ok and vol_ok and rsi_ok and close_strong:
        return True, "EARLY_BUY_EMA50"

    if retest_zone and early_trend_ok and vol_ok and close_strong and rsi_ok:
        return True, "RETEST_BUY"

    if near_breakout and early_trend_ok and (vol_ok or rsi_ok):
        return True, "PREPARE"

    return False, None


# =========================================================
# ATR STOP CALCULATION (NEW)
# =========================================================

def atr_stop_price(close, atr_value, signal):
    """
    Returns recommended stop loss based on ATR.
    """
    if pd.isna(atr_value) or atr_value <= 0:
        return None

    if signal == "EARLY_BUY":
        mult = ATR_MULT_EARLY
    elif signal == "CONFIRM_BUY":
        mult = ATR_MULT_CONFIRM
    elif signal == "RETEST_BUY":
        mult = ATR_MULT_RETEST
    else:
        return None

    return close - (atr_value * mult)


# =========================================================
# SIGNAL
# =========================================================

def technical_signal(df, lookback=LOOKBACK, strictness=STRICTNESS):
    df = add_indicators(df)
    last = df.iloc[-1]

    if pd.isna(last["RSI_WILDER"]) or pd.isna(last["EMA50"]) or pd.isna(last["AvgVol20"]):
        return "NO_TRADE"

    params = get_liberal_params(strictness)
    required = strictness_required_score(strictness)

    prev_high = df["HIGH"].iloc[-lookback-1:-1].max()

    breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok, close_strong, retest_zone = evaluate_conditions(
        last, prev_high, params
    )

    conditions = [breakout, vol_ok, early_trend_ok, rsi_ok]
    score = sum(bool(x) for x in conditions)

    confirm_2day = two_day_breakout_confirm(df, lookback)

    buy, reason = should_buy_signal(
        breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok,
        rsi_ok, close_strong, retest_zone,
        score, required,
        confirm_2day
    )

    if not buy:
        return "NO_TRADE"

    if reason == "CONFIRM_BUY_EMA200":
        return "CONFIRM_BUY"
    if reason == "EARLY_BUY_EMA50":
        return "EARLY_BUY"
    if reason == "RETEST_BUY":
        return "RETEST_BUY"
    if reason == "PREPARE":
        return "PREPARE"

    return "NO_TRADE"


# =========================================================
# DEBUG
# =========================================================

def debug_conditions(df, lookback=LOOKBACK, strictness=STRICTNESS):
    df = add_indicators(df)
    last = df.iloc[-1]

    if pd.isna(last["RSI_WILDER"]):
        print("\n🔍 CONDITION CHECK (LAST CANDLE)")
        print("RSI not ready – insufficient data")
        return

    params = get_liberal_params(strictness)
    required = strictness_required_score(strictness)

    prev_high = df["HIGH"].iloc[-lookback-1:-1].max()

    breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok, rsi_ok, close_strong, retest_zone = evaluate_conditions(
        last, prev_high, params
    )

    conditions = [breakout, vol_ok, early_trend_ok, rsi_ok]
    score = sum(bool(x) for x in conditions)

    confirm_2day = two_day_breakout_confirm(df, lookback)

    buy, reason = should_buy_signal(
        breakout, near_breakout, vol_ok, early_trend_ok, ema200_ok,
        rsi_ok, close_strong, retest_zone,
        score, required,
        confirm_2day
    )

    signal = "NO_TRADE"
    if buy:
        if reason == "CONFIRM_BUY_EMA200":
            signal = "CONFIRM_BUY"
        elif reason == "EARLY_BUY_EMA50":
            signal = "EARLY_BUY"
        elif reason == "RETEST_BUY":
            signal = "RETEST_BUY"
        elif reason == "PREPARE":
            signal = "PREPARE"

    atr_val = last["ATR14"]
    atr_stop = atr_stop_price(last["CLOSE"], atr_val, signal)

    print("\n🔍 CONDITION CHECK (LAST CANDLE)")
    print("Strictness Mode:", strictness)
    print("Breakout:", breakout)
    print("Near Breakout:", near_breakout)
    print("Volume Spike:", vol_ok)
    print("Early Trend OK (EMA50):", early_trend_ok)
    print("Above EMA200:", ema200_ok)
    print("RSI OK:", rsi_ok)
    print("Close Strong:", close_strong)
    print("Retest Zone:", retest_zone)
    print("2-Day Confirm (only for CONFIRM_BUY):", confirm_2day)
    print("BUY Logic:", buy, "| Reason:", reason)

    print("\n📌 ATR INFO")
    print("ATR14:", round(atr_val, 2) if not pd.isna(atr_val) else atr_val)
    if atr_stop:
        print("ATR Stop (Recommended):", round(atr_stop, 2))

    print("\n📌 EXTRA INFO")
    print("Close:", last["CLOSE"])
    print("Prev 20D High:", prev_high)
    print("AvgVol20:", round(last["AvgVol20"], 2))
    print("Volume:", last["VOLUME"])
    print("EMA20:", round(last["EMA20"], 2))
    print("EMA50:", round(last["EMA50"], 2))
    print("EMA200:", round(last["EMA200"], 2))


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    csv_paths = glob.glob("csv file/*.csv")

    for csv_path in csv_paths:
        print(f"\nProcessing: {csv_path}")

        df = load_csv(csv_path)

        debug_conditions(df)
        signal = technical_signal(df)

        print("Signal:", signal)
        print("==================================================================")