
# src/data_fetch/data_fetcher.py
import json
import pandas as pd
from pathlib import Path
from src.config.settings import METADATA_FILE, DATA_RAW_DIR

class DataFetcher:
    def __init__(self):
        self.metadata_path = METADATA_FILE
        self.raw_data_folder = DATA_RAW_DIR

        # Load metadata
        with open(self.metadata_path, "r") as f:
            self.metadata = json.load(f)

    def update_metadata_with_paths(self):
        """Update metadata with historical data file paths."""
        for stock, info in self.metadata.items():
            file_path = self.raw_data_folder / f"{stock}.csv"
            if file_path.exists():
                self.metadata[stock]["historicaldata"] = str(file_path)
            else:
                self.metadata[stock]["historicaldata"] = None

        # Save updated metadata
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=4)
        print("Metadata updated successfully!")

    def fetch_stock_data(self, symbol):
        """Fetch historical data for a single stock."""
        if symbol not in self.metadata:
            raise ValueError(f"Stock {symbol} not found in metadata.")
        file_path = self.metadata[symbol].get("historicaldata")
        if not file_path or not Path(file_path).exists():
            raise FileNotFoundError(f"Historical data file for {symbol} not found.")
        return pd.read_csv(file_path)

    def fetch_all_stocks_data(self):
        """Fetch historical data for all stocks."""
        return {sym: self.fetch_stock_data(sym) for sym in self.metadata.keys()}

