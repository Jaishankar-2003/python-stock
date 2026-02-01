from core.engine import run_system

def main():
    results = run_system(
        nifty_path="data/indices/MW-NIFTY-50-01-Feb-2026.csv",
        sector_paths={
            "IT": "data/sectors/MW-NIFTY-IT-01-Feb-2026.csv"
        },
        stock_paths={
            "IT": {
                "TCS": "data/stocks/Quote-Equity-TCS--01-02-2025-01-02-2026.csv"
            }
        }
    )

    print("\n📊 SYSTEM OUTPUT")
    print(results)

if __name__ == "__main__":
    main()
