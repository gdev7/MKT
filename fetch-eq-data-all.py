import yfinance as yf
import pandas as pd
import os
from tqdm import tqdm   # progress bar

# Create directory to store EOD files
os.makedirs("EOD", exist_ok=True)

# Load NSE equity symbols
equity_details = pd.read_csv("EQUITY_L.csv")

# Loop through each symbol using tqdm
for name in tqdm(equity_details.SYMBOL, desc="Downloading NSE EOD Data"):
    try:
        print(f"\nFetching {name}...")
        data = yf.download(f"{name}.NS", period="20y", progress=False)
        
        if not data.empty:
            data.to_csv(f"./EOD/{name}.csv")
        else:
            print(f"No data for {name}")

    except Exception as e:
        print(f"{name} ===> {e}")
