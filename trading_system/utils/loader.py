import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _to_numeric(series: pd.Series) -> pd.Series:
    """
    Convert NSE-style numeric strings like '25,100.15' to float.
    """
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.strip()
        .pipe(pd.to_numeric, errors="coerce")
    )


def _deduplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    If duplicate columns exist (e.g., multiple 'close'),
    keep the first non-null value row-wise.
    """
    if df.columns.duplicated().any():
        new_df = pd.DataFrame(index=df.index)

        for col in dict.fromkeys(df.columns):  # preserves order
            cols = df.loc[:, df.columns == col]

            if cols.shape[1] == 1:
                new_df[col] = cols.iloc[:, 0]
            else:
                # take first non-null across duplicates
                new_df[col] = cols.bfill(axis=1).iloc[:, 0]

        return new_df

    return df


def load_csv(relative_path: str) -> pd.DataFrame:
    full_path = PROJECT_ROOT / relative_path

    if not full_path.exists():
        raise FileNotFoundError(f"CSV not found: {full_path}")

    df = pd.read_csv(full_path)

    # normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    rename_map = {}

    for col in df.columns:
        c = col.lower()

        # PRICE
        if c in ["close", "close price", "closing price", "indicative close", "ltp"]:
            rename_map[col] = "close"
        elif c in ["prev. close", "previous close"]:
            rename_map[col] = "prev_close"

        elif c in ["open", "open price"]:
            rename_map[col] = "open"
        elif c in ["high", "high price"]:
            rename_map[col] = "high"
        elif c in ["low", "low price"]:
            rename_map[col] = "low"

        # VOLUME
        elif "volume" in c:
            rename_map[col] = "volume"

        # DATE
        elif c in ["date", "timestamp", "trade date"]:
            rename_map[col] = "date"

    df = df.rename(columns=rename_map)

    # 🔑 FIX: collapse duplicate columns (THIS SOLVES YOUR ERROR)
    df = _deduplicate_columns(df)

    # 🔑 NUMERIC SANITIZATION
    for col in ["open", "high", "low", "close", "volume", "prev_close"]:
        if col in df.columns:
            df[col] = _to_numeric(df[col])

    # FINAL VALIDATION
    if "close" not in df.columns:
        raise ValueError(
            f"'close' column missing in {relative_path}. "
            f"Columns found: {list(df.columns)}"
        )

    # sort historical data
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

    return df.reset_index(drop=True)
