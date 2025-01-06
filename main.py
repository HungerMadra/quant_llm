import pandas as pd
from gather_data.nyse_scraper import scrape_nyse
from gather_data.wikipedia_scraper import scrape_wikipedia
from gather_data.polygon_scraper import get_polygon_tickers

# from clean_data.clean_data import clean_tickers  # Future cleaning step

def save_to_csv(data, filename="all_traded_stocks_2014_2019.csv"):
    """Saves the collected tickers to a CSV file."""
    if not data.empty:
        data.to_csv(filename, mode='w', index=False)
        print(f"✅ Data saved to {filename}")

def compile_stock_list():
    print("📊 Fetching NYSE, S&P 500, Nasdaq, and traded stock data...")

    nyse_tickers = scrape_nyse()
    nyse_df = pd.DataFrame(nyse_tickers, columns=["Symbol"])
    nyse_df["Source"] = "NYSE"

    wikipedia_tickers = scrape_wikipedia()
    wikipedia_df = pd.DataFrame(wikipedia_tickers, columns=["Symbol"])
    wikipedia_df["Source"] = "Wikipedia"

    polygon_tickers = get_polygon_tickers()
    polygon_tickers["Source"] = "Polygon"

    all_data = pd.concat([nyse_df, wikipedia_df, polygon_tickers], ignore_index=True)
    print(f"✅ Total tickers collected: {len(all_data)}")

    save_to_csv(all_data)

if __name__ == "__main__":
    compile_stock_list()
