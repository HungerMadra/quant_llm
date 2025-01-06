import pandas as pd

# ✅ Load the collected tickers from CSV
df = pd.read_csv("all_traded_stocks_2014_2019.csv")

# ✅ Ensure tickers are strings, drop duplicates, and remove any invalid values
unique_tickers = df["Symbol"].dropna().astype(str).str.strip().drop_duplicates()

# ✅ Save to `completed_tickers.txt`
with open("completed_tickers.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(unique_tickers))

print(f"✅ Successfully restored {len(unique_tickers)} tickers to completed_tickers.txt")

