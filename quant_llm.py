import yfinance as yf

# Define stock ticker and date range
ticker = "AAPL"
data = yf.download(ticker, start="2014-01-01", end="2015-01-01", interval="1d")

# Display the first few rows
print(data.head())
