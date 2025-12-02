import yfinance as yf
import pandas as pd
import os
import json
from tqdm import tqdm
from src.config import settings

# Create directory to store EOD files
os.makedirs(settings.DATA_RAW_DIR, exist_ok=True)

# Load NSE equity symbols
if os.path.exists(settings.METADATA_FILE):
    with open(settings.METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    equity_details = pd.DataFrame.from_dict(metadata, orient='index')
else:
    print("Metadata file not found.")
    equity_details = pd.DataFrame()

# Loop through each symbol using tqdm
if not equity_details.empty and 'SYMBOL' in equity_details.columns:
    for name in tqdm(equity_details.SYMBOL, desc="Downloading NSE EOD Data"):
        try:
            print(f"\nFetching {name}...")
            data = yf.download(f"{name}.NS", period="20y", progress=False)
            
            if not data.empty:
                data.to_csv(os.path.join(settings.DATA_RAW_DIR, f"{name}.csv"))
            else:
                print(f"No data for {name}")

        except Exception as e:
            print(f"{name} ===> {e}")
else:
    print("No symbols found to process.")
