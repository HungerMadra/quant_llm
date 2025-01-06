import requests
import pandas as pd

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
