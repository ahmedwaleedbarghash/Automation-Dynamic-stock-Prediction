This Python script is a **Data Comparison Tool**.

Its main purpose is to **load all the different stock market CSV files** from your `datasets` folder, combine them into one large dataset, and then **analyze and visualize them** to help you compare your different data sources (Yahoo, Alpha, Kaggle, etc.).

It automatically generates summary reports and charts so you can easily see which data source is the most complete and reliable.

---------

1 **Excellent Data Quality and History:** This file contains Apple (AAPL) stock data from **2010 to 2025**. A long and continuous 15-year history is ideal for training an LSTM model, as it provides ample data for the network to learn complex patterns, seasonality, and long-term trends.
    
2 **Aligns with Project Goals:** Your proposal lists both "Yahoo Finance API" as a primary data source and "Apple (AAPL) Historical Stock Data" as the #1 suggested dataset. This file perfectly matches both criteria.
    
3 **"Hello, World!" of Stock-Prediction:** AAPL is a stable, high-volume stock. It's the standard "baseline" for testing any new time-series model. Your model's performance on AAPL (e.g., its RMSE, MAE) will be a great benchmark before you move to more volatile assets.
    
4 **Clean, Standard Format:** The `yfinance` CSVs are simple, with standard `Date, Open, High, Low, Close, Volume` columns. This requires minimal preprocessing, letting you focus on building the LSTM model itself.