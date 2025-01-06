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


# === 1️⃣ Scrape NYSE Listings from NYSE Website ===
def scrape_nyse():
    """Scrapes all pages of NYSE listings from the official NYSE directory."""
    base_url = "https://www.nyse.com/api/quotes/filter"
    nyse_tickers = set()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "instrumentType": "EQUITY",
        "pageNumber": 1,
        "sortColumn": "NORMALIZED_TICKER",
        "sortOrder": "ASC",
        "maxResultsPerPage": 100
    }

    response = requests.post(base_url, json=payload, headers=headers)
    data = response.json()

    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        total_tickers = data[0].get("total", 0)
    else:
        print("❌ Unexpected NYSE API response format!")
        print(data)
        return []

    max_results_per_page = 100
    total_pages = (total_tickers // max_results_per_page) + (1 if total_tickers % max_results_per_page else 0)

    print(f"📊 NYSE has {total_tickers} tickers across {total_pages} pages.")

    for page in range(1, total_pages + 1):
        print(f"📥 Scraping NYSE directory page {page}/{total_pages}")

        payload["pageNumber"] = page
        response = requests.post(base_url, json=payload, headers=headers)
        data = response.json()

        tickers_found = set()
        for entry in data:
            if isinstance(entry, dict) and "symbolTicker" in entry:
                tickers_found.add(entry["symbolTicker"])

        print(f"✅ Found {len(tickers_found)} tickers on page {page}")
        nyse_tickers.update(tickers_found)

    print(f"✅ Finished! Total NYSE tickers collected: {len(nyse_tickers)}")
    return list(nyse_tickers)


# === 2️⃣ Scrape Wikipedia for NYSE & NASDAQ Listings ===
def scrape_wikipedia():
    """Scrapes Wikipedia pages for NYSE and NASDAQ listings."""
    base_url = "https://en.wikipedia.org/wiki/Companies_listed_on_the_New_York_Stock_Exchange_({})"
    pages = ['0%E2%80%939'] + [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    wikipedia_tickers = set()

    for page in pages:
        url = base_url.format(page)
        print(f"📥 Scraping Wikipedia NYSE page: {url}")

        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Failed to fetch page: {url}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        tickers_found = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "nyse.com/quote/XNYS:" in href or "nasdaq.com/market-activity/stocks/" in href:
                symbol = href.split(":")[-1]
                tickers_found.add(symbol)

        print(f"✅ Found {len(tickers_found)} tickers on {page} page.")
        wikipedia_tickers.update(tickers_found)

    print(f"✅ Finished! Total Wikipedia tickers collected: {len(wikipedia_tickers)}")
    return list(wikipedia_tickers)

def get_polygon_tickers():
    """Fetches all currently traded stock tickers from Polygon.io, handling pagination and rate limits."""
    tickers = []
    base_url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&apiKey={POLYGON_API_KEY}&limit=1000"
    total_tickers = 0  # Track total tickers retrieved

    print("📊 Fetching tickers from Polygon.io...")

    while base_url:
        print(f"📥 Requesting: {base_url}")
        response = requests.get(base_url)
        data = response.json()

        if "results" in data:
            batch_tickers = [stock['ticker'] for stock in data['results']]
            tickers.extend(batch_tickers)
            total_tickers += len(batch_tickers)
            print(f"✅ Retrieved {len(batch_tickers)} tickers. Total so far: {total_tickers}")
        else:
            # Handle rate limit error and retry after waiting
            if "error" in data and "exceeded the maximum requests per minute" in data["error"]:
                print("⏳ Rate limit exceeded. Waiting 60 seconds before retrying...")
                time.sleep(60)  # Wait for 1 minute before retrying
                continue  # Retry the last request

            print(f"❌ Unexpected response from Polygon: {data}")
            break  # Stop fetching if response format is incorrect

        # Check for the next cursor and append API key manually
        next_cursor = data.get("next_url")
        if next_cursor:
            base_url = f"{next_cursor}&apiKey={POLYGON_API_KEY}"
        else:
            break  # No more pages

        time.sleep(1)  # Prevent hitting API rate limits too quickly

    print(f"✅ Finished! Total Polygon tickers collected: {total_tickers}")
    return pd.DataFrame(tickers, columns=['Symbol'])

# === 4️⃣ Save Data to CSV ===
def save_to_csv(data, filename="all_traded_stocks_2014_2019.csv"):
    """Saves the collected tickers to a CSV file."""
    if os.path.exists(filename):
        data.to_csv(filename, mode='a', header=False, index=False)
    else:
        data.to_csv(filename, mode='w', index=False)
    print(f"✅ Data saved to {filename}")


# === 5️⃣ Master Function to Run Everything ===
def compile_stock_list():
    print("📊 Fetching NYSE, S&P 500, Nasdaq, and traded stock data...")

    # ✅ Scrape NYSE Website
    nyse_tickers = scrape_nyse()
    nyse_df = pd.DataFrame(nyse_tickers, columns=["Symbol"])
    nyse_df["Source"] = "NYSE"

    # ✅ Scrape Wikipedia
    wikipedia_tickers = scrape_wikipedia()
    wikipedia_df = pd.DataFrame(wikipedia_tickers, columns=["Symbol"])
    wikipedia_df["Source"] = "Wikipedia"

    # ✅ Fetch Polygon Data (with Logging)
    polygon_tickers = get_polygon_tickers()
    polygon_tickers["Source"] = "Polygon"

    # ✅ Combine all sources
    all_data = pd.concat([nyse_df, wikipedia_df, polygon_tickers], ignore_index=True)
    print(f"✅ Total tickers collected: {len(all_data)}")

    # ✅ Save data
    save_to_csv(all_data)


# === Run the script ===
if __name__ == "__main__":
    compile_stock_list()
