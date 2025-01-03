import os
import yfinance as yf
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time

# === Load API Key from keys.env ===
load_dotenv("keys.env")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

if not POLYGON_API_KEY:
    raise ValueError("Missing POLYGON_API_KEY! Make sure it's in keys.env")

# === 1️⃣ Get S&P 500 and Nasdaq-100 Historical Constituents from Wikipedia ===
def get_sp500_historical():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_df = tables[0]  # First table contains the current S&P 500
    return sp500_df[['Symbol', 'Security', 'GICS Sector']]

def get_nasdaq_100_historical():
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    tables = pd.read_html(url)
    nasdaq_df = tables[4]  # Historical component changes table
    return nasdaq_df[['Ticker', 'Added', 'Removed']]

# === 2️⃣ Get All Traded Stocks from Polygon.io ===
def get_polygon_tickers():
    url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&apiKey={POLYGON_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    tickers = [stock['ticker'] for stock in data.get('results', [])]
    return pd.DataFrame(tickers, columns=['Symbol'])

# === 3️⃣ Get Delisted Stocks from SEC EDGAR ===
def get_sec_delisted_stocks():
    url = "https://www.sec.gov/rules/delist.shtml"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    delisted_stocks = []
    for link in soup.find_all('a'):
        if 'pdf' in link.get('href', ''):
            delisted_stocks.append(link.get_text())

    return pd.DataFrame(delisted_stocks, columns=['Company Name'])

# === 4️⃣ Get IPOs from NASDAQ ===
def get_nasdaq_ipos():
    url = "https://www.nasdaq.com/market-activity/ipos"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    ipos = []
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 1:
            ipo_data = [col.text.strip() for col in cols]
            ipos.append(ipo_data)

    return pd.DataFrame(ipos, columns=['Company Name', 'IPO Date', 'Exchange'])

# === 5️⃣ Filter by IPO and Delisting Dates ===
def filter_by_dates(ipos, delisted):
    ipos['IPO Date'] = pd.to_datetime(ipos['IPO Date'], errors='coerce')
    ipos = ipos[(ipos['IPO Date'] >= "2014-01-01") & (ipos['IPO Date'] <= "2019-12-31")]

    delisted['Delisted Date'] = pd.to_datetime(delisted['Delisted Date'], errors='coerce')
    delisted = delisted[(delisted['Delisted Date'] >= "2014-01-01") & (delisted['Delisted Date'] <= "2019-12-31")]

    return ipos, delisted

# === 6️⃣ Verify Trading Activity via Yahoo Finance ===
def check_stock_activity(ticker):
    try:
        stock = yf.download(ticker, start="2014-01-01", end="2019-12-31", interval="1d")
        return not stock.empty
    except:
        return False

# === 7️⃣ Merge and Save Data ===
def compile_stock_list():
    print("Fetching S&P 500 and Nasdaq historical data...")
    sp500 = get_sp500_historical()
    nasdaq = get_nasdaq_100_historical()

    print("Fetching all traded stocks from Polygon.io...")
    all_tickers = get_polygon_tickers()

    print("Fetching delisted stocks from SEC EDGAR...")
    delisted = get_sec_delisted_stocks()

    print("Fetching IPOs from NASDAQ...")
    ipos = get_nasdaq_ipos()

    print("Filtering by IPO and delisting dates...")
    ipos, delisted = filter_by_dates(ipos, delisted)

    print("Verifying trading activity...")
    verified_tickers = []
    for ticker in all_tickers['Symbol']:
        if check_stock_activity(ticker):
            verified_tickers.append(ticker)
        time.sleep(1)  # Avoid API rate limits

    print("Merging all data sources...")
    combined = pd.concat([sp500, nasdaq, pd.DataFrame(verified_tickers, columns=['Symbol']), delisted, ipos], ignore_index=True)

    print(f"Total unique stocks collected: {combined.shape[0]}")
    
    # Save to CSV
    combined.to_csv("all_traded_stocks_2014_2019.csv", index=False)
    print("Data saved as all_traded_stocks_2014_2019.csv")

# === Run the automation ===
if __name__ == "__main__":
    compile_stock_list()
