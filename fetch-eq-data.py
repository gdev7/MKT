import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
from tqdm import tqdm


class NSEDataFetcher:

    def __init__(self, equity_file="EQUITY_L.csv", folder="EOD"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

        # Load metadata (must contain SYMBOL and TAG columns)
        self.equity_df = pd.read_csv(equity_file)

    # -------------------------------------------------------
    # Utility: Load CSV if exists
    # -------------------------------------------------------
    def _get_file_path(self, symbol):
        return os.path.join(self.folder, f"{symbol}.csv")

    # -------------------------------------------------------
    # 1. Fetch only new data (incremental update)
    # -------------------------------------------------------
    def fetch_latest(self, symbol):
        file_path = self._get_file_path(symbol)

        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path, parse_dates=["Date"])
            last_date = old_df["Date"].max().date()
            start_date = last_date + timedelta(days=1)
        else:
            print(f"No old data found for {symbol}. Use fetch_all().")
            return None

        today = datetime.now().date()
        if start_date > today:
            print(f"{symbol} already up-to-date.")
            return None

        new_data = yf.download(
            f"{symbol}.NS",
            start=start_date,
            end=today + timedelta(days=1),
            progress=False,
        )

        if new_data.empty:
            print(f"No new data for {symbol}.")
            return None

        new_data.reset_index(inplace=True)
        final_df = pd.concat([old_df, new_data]).drop_duplicates("Date").sort_values("Date")
        final_df.to_csv(file_path, index=False)

        print(f"{symbol} updated to {final_df['Date'].max().date()}")
        return final_df

    # -------------------------------------------------------
    # 2. Fetch complete history (default last 20 years)
    # -------------------------------------------------------
    def fetch_all(self, symbol, years=20):
        print(f"Fetching {years} years data for {symbol}...")

        data = yf.download(f"{symbol}.NS", period=f"{years}y", progress=False)

        if data.empty:
            print(f"No data found for {symbol}.")
            return None

        data.reset_index(inplace=True)
        data.to_csv(self._get_file_path(symbol), index=False)
        print(f"{symbol} full history saved.")
        return data

    # -------------------------------------------------------
    # 3. Fetch only today's data
    # -------------------------------------------------------
    def fetch_today(self, symbol):
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        data = yf.download(
            f"{symbol}.NS",
            start=today,
            end=tomorrow,
            progress=False
        )

        if data.empty:
            print(f"No data for {symbol} today.")
            return None

        data.reset_index(inplace=True)
        print(f"Today's data for {symbol} fetched.")
        return data

    # -------------------------------------------------------
    # 4. Fetch data using stock tag (example: largecap)
    # -------------------------------------------------------
    def fetch_by_tag(self, tag, latest=False):
        tagged_symbols = self.equity_df[self.equity_df["TAG"] == tag].SYMBOL.tolist()

        print(f"Found {len(tagged_symbols)} stocks with tag '{tag}'.")

        for symbol in tqdm(tagged_symbols, desc=f"Fetching {tag} stocks"):
            if latest:
                self.fetch_latest(symbol)
            else:
                self.fetch_all(symbol)


# --------------------------------------------------------------------------------
# Example Usage:
# --------------------------------------------------------------------------------
# fetcher = NSEDataFetcher("EQUITY_L.csv")

# fetcher.fetch_latest("RELIANCE")
# fetcher.fetch_all("TCS")
# fetcher.fetch_today("HDFCBANK")
# fetcher.fetch_by_tag("largecap", latest=True)
