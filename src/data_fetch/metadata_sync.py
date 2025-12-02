import os
import json
import pandas as pd
import requests
from datetime import datetime
from src.config import settings
from src.data_fetch.data_fetcher import DataFetcher

class MetadataSync:
    def __init__(self):
        self.equity_csv_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        self.metadata_file = settings.METADATA_FILE
        self.raw_dir = settings.DATA_RAW_DIR
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def download_equity_csv(self):
        """Downloads the latest EQUITY_L.csv from NSE."""
        print(f"Downloading equity list from {self.equity_csv_url}...")
        try:
            response = requests.get(self.equity_csv_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Save to a temporary file or parse directly
            # Let's save it temporarily to data/metadata/EQUITY_L_new.csv
            temp_path = os.path.join(settings.DATA_METADATA_DIR, "EQUITY_L_new.csv")
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            print("Download successful.")
            return temp_path
        except Exception as e:
            print(f"Error downloading equity CSV: {e}")
            return None

    def sync_metadata(self):
        """
        Downloads latest equity list, updates stocks_metadata.json,
        and identifies new/deleted stocks.
        """
        csv_path = self.download_equity_csv()
        if not csv_path:
            return

        # Load new CSV
        try:
            new_df = pd.read_csv(csv_path)
            # Clean column names just in case
            new_df.columns = [c.strip() for c in new_df.columns]
        except Exception as e:
            print(f"Error reading downloaded CSV: {e}")
            return

        # Load existing metadata
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                old_metadata = json.load(f)
        else:
            old_metadata = {}

        # Convert new DF to dict: SYMBOL -> metadata
        new_metadata = {}
        for _, row in new_df.iterrows():
            symbol = row["SYMBOL"]
            new_metadata[symbol] = row.to_dict()

        # Identify changes
        old_symbols = set(old_metadata.keys())
        new_symbols = set(new_metadata.keys())

        added_symbols = new_symbols - old_symbols
        deleted_symbols = old_symbols - new_symbols
        
        print(f"Found {len(added_symbols)} new stocks.")
        print(f"Found {len(deleted_symbols)} deleted stocks.")

        # Update JSON file
        with open(self.metadata_file, "w") as f:
            json.dump(new_metadata, f, indent=4)
        print(f"Updated {self.metadata_file}")

        # Sync raw data files
        self.sync_data_files(added_symbols, deleted_symbols)

        # Cleanup
        if os.path.exists(csv_path):
            os.remove(csv_path)

    def sync_data_files(self, added_symbols, deleted_symbols):
        """
        Adds new CSVs for added stocks and removes CSVs for deleted stocks.
        """
        fetcher = DataFetcher()

        # 1. Handle Deleted Stocks
        for symbol in deleted_symbols:
            file_path = os.path.join(self.raw_dir, f"{symbol}.csv")
            if os.path.exists(file_path):
                print(f"Removing data for deleted stock: {symbol}")
                os.remove(file_path)

        # 2. Handle New Stocks
        if added_symbols:
            print(f"Fetching initial data for {len(added_symbols)} new stocks...")
            for symbol in added_symbols:
                print(f"Initializing data for {symbol}...")
                fetcher.fetch_all(symbol)

        print("Data files sync complete.")
