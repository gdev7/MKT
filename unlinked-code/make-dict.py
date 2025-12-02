import pandas as pd
import os
import json

# Load CSV
df = pd.read_csv("equity_L.csv")

# Create output folder
os.makedirs("EQDATA", exist_ok=True)

# Iterate through each stock and create a dict file
for _, row in df.iterrows():
    symbol = row["SYMBOL"]
    
    stock_dict = {
        "SYMBOL": row["SYMBOL"],
        "NAME OF COMPANY": row["NAME OF COMPANY"],
        "DATE OF LISTING": row["DATE OF LISTING"]
    }

    # Save each dict as a JSON file
    file_path = f"./EQDATA/{symbol}.json"
    with open(file_path, "w") as f:
        json.dump(stock_dict, f, indent=4)

    print(f"Created: {symbol}.json")

