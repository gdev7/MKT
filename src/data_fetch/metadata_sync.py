import os
import json
import pandas as pd
import requests
import io
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
        # We want to MERGE with existing metadata to preserve custom fields like INDICES
        new_metadata = {}
        for _, row in new_df.iterrows():
            symbol = row["SYMBOL"]
            row_data = row.to_dict()
            
            if symbol in old_metadata:
                # Start with existing data
                merged_data = old_metadata[symbol].copy()
                # Update with new data from CSV (overwriting NSE fields)
                merged_data.update(row_data)
                new_metadata[symbol] = merged_data
            else:
                # New stock
                new_metadata[symbol] = row_data

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

    def update_index_constituents(self, index_name, csv_url):
        """
        Updates stocks_metadata.json with index information from a given NSE CSV URL.
        """
        print(f"Updating constituents for index: {index_name} from {csv_url}")
        
        try:
            # Use a session to handle potential cookie requirements
            session = requests.Session()
            session.headers.update(self.headers)
            # Visit homepage first
            session.get("https://www.nseindia.com")
            
            response = session.get(csv_url)
            response.raise_for_status()
            content = response.text
            
            # Robust parsing strategy
            # Find the start of data - usually the index name is in the first column of the first data row
            # But the header is messy. Let's look for the index name in quotes as a marker if possible,
            # or just try to find the header line if we knew it.
            # Based on testing, finding the index name string works well as a data start marker.
            
            # However, the index name in the CSV might be slightly different or just "NIFTY SMALLCAP 100"
            # Let's try to find the start of the data by looking for the first line that looks like data
            # or by stripping the bad header.
            
            # Strategy from testing: Find the index name in the content
            # The CSV usually starts with metadata/garbage and then the actual data rows start.
            # The first column is "SYMBOL" (or similar) in the header, but the header is broken.
            # The first data row usually contains the index name in the first column? 
            # Wait, in the test output: "NIFTY SMALLCAP 100","17,875.70"...
            # And then "NATCOPHARM","907.70"...
            # So the first row is the index itself, and subsequent rows are stocks.
            # We need to extract symbols from the subsequent rows.
            
            # Let's find the line that starts with "NIFTY SMALLCAP 100" (or whatever the index name is)
            # and treat that as the start of data (or the line before it as header).
            # Actually, we can just look for the "SYMBOL" column if we clean the header, 
            # but the header was broken.
            
            # Let's use the strategy that worked: Find the index name, treat that as start of data,
            # prepend a clean header.
            
            # Note: The index name in the CSV might be quoted.
            search_marker = f'"{index_name}"'
            start_index = content.find(search_marker)
            
            if start_index == -1:
                # Try without quotes
                search_marker = index_name
                start_index = content.find(search_marker)
                
            if start_index == -1:
                print(f"Could not find data start marker '{index_name}' in response.")
                return

            raw_data = content[start_index:]
            
            # Define clean header
            clean_header = '"SYMBOL","OPEN","HIGH","LOW","PREV. CLOSE","LTP","INDICATIVE CLOSE","CHNG","%CHNG","VOLUME","VALUE","52W H","52W L","30 D %CHNG","365 D % CHNG"\n'
            final_csv = clean_header + raw_data
            
            df = pd.read_csv(io.StringIO(final_csv))
            
            # Filter out the index itself if it appears as a row (it usually does as the first row)
            # The index row usually has the index name in the SYMBOL column
            df = df[df["SYMBOL"] != index_name]
            
            symbols_in_index = df["SYMBOL"].tolist()
            print(f"Found {len(symbols_in_index)} stocks in {index_name}")
            
            # Update metadata
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r") as f:
                    metadata = json.load(f)
            else:
                print("Metadata file not found. Please run sync_metadata first.")
                return
                
            updated_count = 0
            for symbol in symbols_in_index:
                if symbol in metadata:
                    if "INDICES" not in metadata[symbol]:
                        metadata[symbol]["INDICES"] = []
                    
                    if index_name not in metadata[symbol]["INDICES"]:
                        metadata[symbol]["INDICES"].append(index_name)
                        updated_count += 1
                else:
                    print(f"Warning: Stock {symbol} from index {index_name} not found in master metadata.")
            
            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=4)
                
            print(f"Updated {updated_count} stocks with {index_name} tag.")
            
        except Exception as e:
            print(f"Error updating index constituents: {e}")
