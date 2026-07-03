"""
Fetch portfolio price history and generate CSVs for the Power BI dashboard.

Setup:
    pip install yfinance pandas

Run:
    python fetch_portfolio_data.py

Outputs:
    transactions.csv    -> your buy/sell history (edit TRANSACTIONS below with real trades)
    daily_prices.csv    -> daily closing price + daily return for every ticker you hold
"""

import pandas as pd
import yfinance as yf
from datetime import date

# ---------------------------------------------------------------------------
# 1. YOUR TRANSACTIONS
# Replace this list with your actual (or realistic simulated) trade history.
# type: "BUY" or "SELL"
# ---------------------------------------------------------------------------
TRANSACTIONS = [
    {"date": "2023-01-10", "ticker": "AAPL", "type": "BUY", "quantity": 10, "price": 130.73},
    {"date": "2023-03-15", "ticker": "MSFT", "type": "BUY", "quantity": 8,  "price": 265.44},
    {"date": "2023-05-02", "ticker": "VOO",  "type": "BUY", "quantity": 15, "price": 372.10},
    {"date": "2023-07-20", "ticker": "GOOGL","type": "BUY", "quantity": 12, "price": 121.99},
    {"date": "2023-09-11", "ticker": "AAPL", "type": "BUY", "quantity": 5,  "price": 176.55},
    {"date": "2023-11-30", "ticker": "BTC-USD","type": "BUY", "quantity": 0.15, "price": 37800.00},
    {"date": "2024-02-14", "ticker": "MSFT", "type": "BUY", "quantity": 4,  "price": 415.26},
    {"date": "2024-06-05", "ticker": "AAPL", "type": "SELL","quantity": 5,  "price": 194.35},
    {"date": "2024-10-18", "ticker": "VOO",  "type": "BUY", "quantity": 10, "price": 542.30},
    {"date": "2025-02-27", "ticker": "GOOGL","type": "BUY", "quantity": 6,  "price": 173.80},
]

# ---------------------------------------------------------------------------
# 2. SAVE TRANSACTIONS.CSV
# ---------------------------------------------------------------------------
txn_df = pd.DataFrame(TRANSACTIONS)
txn_df["date"] = pd.to_datetime(txn_df["date"])
txn_df = txn_df.sort_values("date")
txn_df.to_csv("transactions.csv", index=False)
print(f"Saved transactions.csv ({len(txn_df)} rows)")

# ---------------------------------------------------------------------------
# 3. FETCH DAILY PRICE HISTORY FOR EVERY TICKER YOU'VE TRADED
# ---------------------------------------------------------------------------
tickers = sorted(txn_df["ticker"].unique().tolist())
start_date = txn_df["date"].min().strftime("%Y-%m-%d")
end_date = date.today().strftime("%Y-%m-%d")

print(f"\nFetching daily prices for {tickers}")
print(f"Date range: {start_date} to {end_date}\n")

all_prices = []

for ticker in tickers:
    print(f"  downloading {ticker}...")
    hist = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)

    if hist.empty:
        print(f"  WARNING: no data returned for {ticker}, skipping")
        continue

    hist = hist.reset_index()
    # yfinance sometimes returns MultiIndex columns when multiple tickers are involved
    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = [c[0] for c in hist.columns]

    df = hist[["Date", "Close"]].copy()
    df.columns = ["date", "close_price"]
    df["ticker"] = ticker
    df["daily_return"] = df["close_price"].pct_change()
    all_prices.append(df)

prices_df = pd.concat(all_prices, ignore_index=True)
prices_df = prices_df[["date", "ticker", "close_price", "daily_return"]]
prices_df["date"] = pd.to_datetime(prices_df["date"]).dt.date
prices_df.to_csv("daily_prices.csv", index=False)

print(f"\nSaved daily_prices.csv ({len(prices_df)} rows across {len(tickers)} tickers)")
print("\nDone. Import both CSVs into Power BI:")
print("  transactions.csv  -> Fact_Transactions")
print("  daily_prices.csv  -> Fact_DailyPrices")
print("Build a Date dimension table in Power BI (CALENDAR/CALENDARAUTO) and relate both facts to it.")
