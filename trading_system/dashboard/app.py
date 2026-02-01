import dash
from dash import html, dcc, dash_table
import pandas as pd

from core.engine import run_system

app = dash.Dash(__name__)

output = run_system(
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

# normalize output
if isinstance(output, dict):
    df = pd.DataFrame([output])
elif isinstance(output, list):
    df = pd.DataFrame(output)
else:
    df = pd.DataFrame()

app.layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H2("📊 Swing Trading Dashboard"),

        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in df.columns],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
