# # ====================================================
# # Dynamic Stock Price Datasets Downloader
# # Author: Ahmed Barghash
# # Project: Dynamic Stock Price Prediction System
# # ====================================================

# import yfinance as yf
# import os

# # Create datasets folder
# os.makedirs("datasets", exist_ok=True)

# # List of tickers to download
# tickers = {
#     "Apple (AAPL)": "AAPL",
#     "Microsoft (MSFT)": "MSFT",
#     "Amazon (AMZN)": "AMZN",
#     "Google (GOOGL)": "GOOGL",
#     "Tesla (TSLA)": "TSLA",
#     "S&P 500 (^GSPC)": "^GSPC",
#     "Bitcoin (BTC-USD)": "BTC-USD",
#     "Nifty 50 (NSEI)": "^NSEI"  # Indian Stock Market Index
# }

# # Date range
# start_date = "2010-01-01"
# end_date = "2025-10-26"

# print("📊 Starting dataset download...\n")

# for name, ticker in tickers.items():
#     print(f"Downloading {name} ({ticker}) ...")
#     data = yf.download(ticker, start=start_date, end=end_date)
#     file_name = f"datasets/{ticker.replace('^', '')}_data.csv"
#     data.to_csv(file_name)
#     print(f"✅ Saved to {file_name}\n")

# print("🎉 All datasets downloaded successfully!")

# ====================================================

# ====================================================
# Alpha Vantage Multi-Stock Dataset Downloader
# Author: Ahmed Barghash
# Project: Dynamic Stock Price Prediction System
# ====================================================

# from alpha_vantage.timeseries import TimeSeries
# import os
# import time

# # Initialize Alpha Vantage connection
# API_KEY = 'J9IWAJYMAS6W0S1S'
# ts = TimeSeries(key=API_KEY, output_format='pandas')

# # Create datasets folder if not exists
# os.makedirs("datasets/alpha_vantage", exist_ok=True)

# # List of tickers to download (8 datasets)
# tickers = {
#     "Apple (AAPL)": "AAPL",
#     "Google (GOOGL)": "GOOGL",
#     "Microsoft (MSFT)": "MSFT",
#     "Tesla (TSLA)": "TSLA",
#     "Amazon (AMZN)": "AMZN",
#     "S&P 500 (^GSPC)": "SPY",      # S&P 500 ETF proxy
#     "Bitcoin (BTC-USD)": "BTC-USD",
#     "Nifty 50 (NSEI)": "NSEI"      # Indian stock market
# }

# print("📈 Downloading datasets from Alpha Vantage...\n")

# for name, symbol in tickers.items():
#     try:
#         print(f"⏳ Downloading {name} ({symbol}) ...")
#         data, meta = ts.get_daily(symbol=symbol, outputsize='full')
#         filename = f"datasets/alpha_vantage/{symbol}_data.csv"
#         data.to_csv(filename)
#         print(f"✅ Saved to {filename}\n")
#         time.sleep(12)  # Alpha Vantage limit: 5 API calls per minute
#     except Exception as e:
#         print(f"❌ Error downloading {name}: {e}\n")

# print("🎉 All Alpha Vantage datasets downloaded successfully!")

# ====================================================

# ====================================================
# Dynamic Stock Price Datasets Downloader
# Author: Ahmed Barghash
# Project: Dynamic Stock Price Prediction System
# ====================================================

# import os
# import pandas as pd
# import finnhub

# # Create datasets folder
# os.makedirs("datasets", exist_ok=True)

# # ===============================
# # FINNHUB DATA DOWNLOAD SECTION
# # ===============================

# print("📈 Starting Finnhub dataset download...\n")

# # Initialize Finnhub connection
# finnhub_client = finnhub.Client(api_key="d3v7g71r01qt2ctoes6gd3v7g71r01qt2ctoes70")

# # List of tickers to download
# tickers = {
#     "Apple (AAPL)": "AAPL",
#     "Microsoft (MSFT)": "MSFT",
#     "Amazon (AMZN)": "AMZN",
#     "Google (GOOGL)": "GOOGL",
#     "Tesla (TSLA)": "TSLA",
# }

# # Time range in UNIX timestamps (2020-01-01 → 2025-10-26)
# start_date = int(pd.Timestamp("2020-01-01").timestamp())
# end_date = int(pd.Timestamp("2025-10-26").timestamp())

# for name, ticker in tickers.items():
#     print(f"Downloading {name} ({ticker}) ...")
#     try:
#         res = finnhub_client.stock_candles(ticker, 'D', start_date, end_date)
#         df = pd.DataFrame(res)
#         if 't' in df.columns:
#             df['t'] = pd.to_datetime(df['t'], unit='s')
#             df.rename(columns={'t': 'Date'}, inplace=True)
#         file_name = f"datasets/{ticker}_finnhub.csv"
#         df.to_csv(file_name, index=False)
#         print(f"✅ Saved to {file_name}\n")
#     except Exception as e:
#         print(f"❌ Error downloading {ticker}: {e}\n")

# print("🎉 Finnhub datasets downloaded successfully!")

# ====================================================

# File: download_polygon.py
import pandas as pd
from polygon import RESTClient
from datetime import date, timedelta
import os

# --- 1. CONFIGURATION ---
# ⚠️ PASTE YOUR POLYGON API KEY HERE
POLYGON_KEY = "ysc_xtZSwHRcEkeVDojKQHJNsHorO38k" 

TICKERS = ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL", "SPY", "QQQ"]
OUTPUT_DIR = "datasets"

# Set date range (Polygon's free tier gives ~2 years of daily data)
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=2 * 365)

# Format for API
START_STR = START_DATE.strftime("%Y-%m-%d")
END_STR = END_DATE.strftime("%Y-%m-%d")

print(f"Connecting to Polygon.io to download data from {START_STR} to {END_STR}...")

# --- 2. CREATE CLIENT ---
try:
    client = RESTClient(POLYGON_KEY)
except Exception as e:
    print(f"Error connecting to Polygon: {e}")
    print("Please make sure your API key is correct in POLYGON_KEY.")
    exit()

# --- 3. DOWNLOAD LOOP ---
for ticker in TICKERS:
    print(f"\nFetching {ticker} from Polygon...")
    try:
        # Get aggregates (daily bars)
        resp = client.get_aggs(
            ticker,
            1,
            "day",
            START_STR,
            END_STR,
            limit=50000
        )

        if not resp:
            print(f"No data returned for {ticker}. Skipping.")
            continue

        # Convert to DataFrame
        df = pd.DataFrame(resp)
        
        # Rename columns to match your standard format
        df['Date'] = pd.to_datetime(df['t'], unit='ms').dt.date
        df.rename(columns={
            'o': 'Open',
            'h': 'High',
            'l': 'Low',
            'c': 'Close',
            'v': 'Volume'
        }, inplace=True)
        
        # Keep only the standard columns
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

        # Save to CSV with the '_polygon.csv' suffix
        filename = os.path.join(OUTPUT_DIR, f"{ticker}_polygon.csv")
        df.to_csv(filename, index=False)
        print(f"✅ Saved {len(df)} records to {filename}")

    except Exception as e:
        print(f"❌ Error downloading {ticker}: {e}")

print("\nPolygon download complete.")