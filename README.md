# Personal Investment Portfolio Dashboard

An interactive Power BI dashboard that tracks a personal investment portfolio (stocks, ETFs, and crypto) using real historical market data. Built end-to-end: Python data pipeline → star schema data model → DAX measures → dashboard design.

## What it does

The dashboard answers four questions at a glance:

- **How much have I invested, and what's it worth today?**
- **How has my portfolio's value changed over time?**
- **How is my money allocated across holdings?**
- **Which positions are performing best?**

It updates from real market prices, so the numbers reflect what actually happened in the market over the tracked period — not simulated growth curves.

## Data pipeline

Historical price data is pulled with a Python script (`fetch_portfolio_data.py`) using the `yfinance` library:

- Takes a list of transactions (ticker, date, buy/sell, quantity, price)
- Downloads daily closing prices for every ticker traded, from the first transaction date to today
- Outputs two clean CSVs: `transactions.csv` and `daily_prices.csv`

This mirrors a real-world ETL step — pulling from an external source, shaping it, and handing off a clean, analysis-ready dataset — rather than starting from a pre-cleaned sample file.

## Data model

The dataset is modeled as a star schema in Power BI:

- **Dim_Date** — calendar table with year, quarter, month, and week attributes, generated with `CALENDAR()`
- **Dim_Security** — one row per ticker, built with `DISTINCT(UNION(...))` across both fact tables
- **Fact_Transactions** — every buy/sell trade (date, ticker, type, quantity, price)
- **Fact_DailyPrices** — daily closing price and daily return per ticker

Two dimension tables connect to both fact tables. One relationship (Dim_Security → daily_prices) is set inactive to avoid a circular filter path between the four tables — a deliberate modeling choice rather than an oversight, since Power BI can't resolve ambiguous loops between tables.

## Key DAX measures

- `Shares Held` — running total of shares owned per ticker, accounting for buys and sells
- `Latest Price` — most recent close price per ticker, resolved independently of the inactive relationship using `FILTER(ALL(...))`
- `Portfolio Value` / `Position Value` — shares held × latest price, at the portfolio and per-ticker level
- `Total Invested`, `Total Return`, `Total Return %` — cost basis and performance
- `Daily Portfolio Value` — the most complex measure: for every date on the X-axis, it recalculates shares owned as of that date and the applicable price as of that date, using `SUMX` over `VALUES()` with date-filtered `CALCULATE()` logic. This is what powers the trend line.

The trend line is plotted at a weekly grain (`WeekStart`, derived from `Dim_Date`) rather than daily — daily granularity produced too much visual noise to read as a trend, so the model aggregates up for clarity without losing the underlying shape of portfolio growth.

## Dashboard layout

- **KPI row** — Total Invested, Portfolio Value, Total Return, Total Return %
- **Trend line** — portfolio value over time, weekly
- **Donut chart** — allocation by ticker
- **Holdings table** — shares held, latest price, position value, and return % per ticker

## A few insights the dashboard surfaces

- BTC-USD represents a disproportionate share of total portfolio value relative to its original cost basis — a small position size but outsized contribution to overall return, which is visible immediately in the donut chart despite not being obvious from the transaction log alone.
- VOO (a broad market ETF) is the single largest position by value, acting as the portfolio's stability anchor against the more volatile individual stock and crypto positions.

## Tools used

Python (`yfinance`, `pandas`) for data extraction · Power BI Desktop for modeling, DAX, and visualization

## Possible extensions

- Benchmark comparison line (e.g. vs. S&P 500) on the trend chart
- Rolling volatility or Sharpe ratio measures
- A ticker slicer for filtering the whole dashboard to a single holding
- Scheduled refresh via Power BI Service if connected to a live data source
