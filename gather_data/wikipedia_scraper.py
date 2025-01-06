import requests
import pandas as pd
from bs4 import BeautifulSoup

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
