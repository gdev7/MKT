import yfinance as yf
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from tqdm import tqdm
from src.config import settings

class NSEDataFetcher:

    def __init__(self):
        self.folder = settings.DATA_RAW_DIR
        self.metadata_file = settings.METADATA_FILE
        
        # Load metadata
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
            # Convert to DataFrame for easier querying if needed, or just use dict
            # For compatibility with existing logic, let's make a DataFrame
            self.equity_df = pd.DataFrame.from_dict(self.metadata, orient='index')
        else:
            print(f"Metadata file not found at {self.metadata_file}")
            self.metadata = {}
            self.equity_df = pd.DataFrame()

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
            if not old_df.empty:
                last_date = old_df["Date"].max().date()
                start_date = last_date + timedelta(days=1)
            else:
                # File exists but empty
                start_date = datetime(2000, 1, 1).date()
        else:
            print(f"No old data found for {symbol}. Use fetch_all().")
            return None

        today = datetime.now().date()
        if start_date > today:
            print(f"{symbol} already up-to-date.")
            return None

        print(f"Fetching data for {symbol} from {start_date} to {today}")
        try:
            new_data = yf.download(
                f"{symbol}.NS",
                start=start_date,
                end=today + timedelta(days=1),
                progress=False,
            )
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

        if new_data.empty:
            print(f"No new data for {symbol}.")
            return None

        new_data.reset_index(inplace=True)
        # Ensure Date column is datetime
        if 'Date' not in new_data.columns:
             # yfinance sometimes puts Date in index
             pass 
        
        # Handle MultiIndex columns if present (yfinance update)
        if isinstance(new_data.columns, pd.MultiIndex):
            new_data.columns = new_data.columns.get_level_values(0)

        if os.path.exists(file_path):
             old_df = pd.read_csv(file_path, parse_dates=["Date"])
             final_df = pd.concat([old_df, new_data]).drop_duplicates("Date").sort_values("Date")
        else:
             final_df = new_data

        final_df.to_csv(file_path, index=False)

        print(f"{symbol} updated to {final_df['Date'].max().date()}")
        return final_df

    # -------------------------------------------------------
    # 2. Fetch complete history (default last 20 years)
    # -------------------------------------------------------
    def fetch_all(self, symbol, years=20):
        print(f"Fetching {years} years data for {symbol}...")

        try:
            data = yf.download(f"{symbol}.NS", period=f"{years}y", progress=False)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

        if data.empty:
            print(f"No data found for {symbol}.")
            return None

        data.reset_index(inplace=True)
        # Handle MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        data.to_csv(self._get_file_path(symbol), index=False)
        print(f"{symbol} full history saved.")
        return data

    # -------------------------------------------------------
    # 3. Fetch only today's data
    # -------------------------------------------------------
    def fetch_today(self, symbol):
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        try:
            data = yf.download(
                f"{symbol}.NS",
                start=today,
                end=tomorrow,
                progress=False
            )
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

        if data.empty:
            print(f"No data for {symbol} today.")
            return None

        data.reset_index(inplace=True)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        print(f"Today's data for {symbol} fetched.")
        return data

    # -------------------------------------------------------
    # 4. Fetch data using stock tag (example: largecap)
    # -------------------------------------------------------
    def fetch_by_tag(self, tag, latest=False):
        if "TAG" not in self.equity_df.columns:
            print("TAG column not found in metadata.")
            return

        tagged_symbols = self.equity_df[self.equity_df["TAG"] == tag].SYMBOL.tolist()

        print(f"Found {len(tagged_symbols)} stocks with tag '{tag}'.")

        for symbol in tqdm(tagged_symbols, desc=f"Fetching {tag} stocks"):
            if latest:
                self.fetch_latest(symbol)
            else:
                self.fetch_all(symbol)
