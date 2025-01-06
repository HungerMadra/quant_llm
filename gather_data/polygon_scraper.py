import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv("keys.env")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

if not POLYGON_API_KEY:
    raise ValueError("Missing POLYGON_API_KEY! Make sure it's in keys.env")

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
            if "error" in data and "exceeded the maximum requests per minute" in data["error"]:
                print("⏳ Rate limit exceeded. Waiting 60 seconds before retrying...")
                time.sleep(60)
                continue

            print(f"❌ Unexpected response from Polygon: {data}")
            break

        next_cursor = data.get("next_url")
        if next_cursor:
            base_url = f"{next_cursor}&apiKey={POLYGON_API_KEY}"
        else:
            break

        time.sleep(1)

    print(f"✅ Finished! Total Polygon tickers collected: {total_tickers}")
    return pd.DataFrame(tickers, columns=['Symbol'])
