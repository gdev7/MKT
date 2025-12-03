import json
import urllib.parse
import requests
import csv
import os
import time
import argparse
import sys

# Constants
BASE_URL = "https://www.nseindia.com/api/equity-stockIndices?csv=true&index={}&selectValFormat=crores"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nseindia.com/'
}

def get_paths():
    """Returns a dictionary of relevant file paths."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Go up one level from scripts/
    return {
        "indices_list": os.path.join(base_dir, "data", "metadata", "indices_list.txt"),
        "indices_config": os.path.join(base_dir, "data", "metadata", "indices_config.json"),
        "stocks_metadata": os.path.join(base_dir, "data", "metadata", "stocks_metadata.json")
    }

def update_indices_config():
    """Reads indices_list.txt and generates indices_config.json."""
    paths = get_paths()
    list_path = paths["indices_list"]
    config_path = paths["indices_config"]
    
    print(f"Reading indices list from: {list_path}")
    if not os.path.exists(list_path):
        print(f"Error: {list_path} not found.")
        return

    with open(list_path, 'r') as f:
        indices = [line.strip() for line in f if line.strip()]

    config = []
    for name in indices:
        encoded = urllib.parse.quote(name)
        url = BASE_URL.format(encoded)
        config.append({"name": name, "url": url})

    # Ensure directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"Successfully updated {config_path} with {len(config)} indices.")

def update_stocks_metadata():
    """Reads indices_config.json, downloads CSVs, and updates stocks_metadata.json."""
    paths = get_paths()
    config_path = paths["indices_config"]
    metadata_path = paths["stocks_metadata"]
    
    print(f"Reading config from: {config_path}")
    if not os.path.exists(config_path):
        print("Config file not found! Please run with --refresh-config first.")
        return

    with open(config_path, 'r') as f:
        indices_config = json.load(f)

    print(f"Updating metadata at: {metadata_path}")
    
    # Load existing metadata
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            try:
                metadata = json.load(f)
            except json.JSONDecodeError:
                print("Error decoding existing metadata. Starting fresh.")
                metadata = {}
    else:
        print("Metadata file not found. Starting fresh.")
        metadata = {}

    session = requests.Session()
    session.headers.update(HEADERS)
    
    # Visit homepage to get cookies
    print("Visiting NSE homepage to establish session...")
    try:
        session.get("https://www.nseindia.com", timeout=30)
    except Exception as e:
        print(f"Error visiting homepage: {e}")
        return

    for index_info in indices_config:
        index_name = index_info['name']
        url = index_info['url']
        print(f"Processing {index_name}...")
        
        try:
            response = session.get(url, timeout=30)
            if response.status_code == 200:
                csv_content = response.content.decode('utf-8')
                
                lines = csv_content.splitlines()
                # Find the header line
                header_index = -1
                for i, line in enumerate(lines):
                    if "Symbol" in line:
                        header_index = i
                        break
                
                if header_index != -1:
                    csv_reader = csv.DictReader(lines[header_index:])
                    # Clean field names
                    csv_reader.fieldnames = [x.strip().replace('"', '') for x in csv_reader.fieldnames]
                    
                    for row in csv_reader:
                        symbol = row.get('Symbol', '').strip()
                        if not symbol:
                            continue
                            
                        if symbol not in metadata:
                            metadata[symbol] = {
                                "SYMBOL": symbol,
                                "NAME OF COMPANY": row.get('Company Name', ''),
                                "SERIES": row.get('Series', 'EQ'),
                                "ISIN NUMBER": row.get('ISIN Code', ''),
                                "FACE VALUE": row.get('Face Value', ''),
                                "PAID UP VALUE": row.get('Paid Up Value', ''),
                                "MARKET LOT": 1, # Default
                                "DATE OF LISTING": row.get('Listing Date', '') 
                            }
                        
                        if "INDICES" not in metadata[symbol]:
                            metadata[symbol]["INDICES"] = []
                        
                        if index_name not in metadata[symbol]["INDICES"]:
                            metadata[symbol]["INDICES"].append(index_name)
                else:
                    print(f"Could not find CSV header for {index_name}")
            else:
                print(f"Failed to fetch {index_name}: Status {response.status_code}")
            
            # Be nice to the server
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {index_name}: {e}")

    # Save metadata
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    print("Metadata updated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Manage market data updates.")
    parser.add_argument("--refresh-config", action="store_true", help="Regenerate indices_config.json from indices_list.txt")
    parser.add_argument("--refresh-metadata", action="store_true", help="Download stock data and update stocks_metadata.json")
    
    args = parser.parse_args()

    if args.refresh_config:
        update_indices_config()
    
    if args.refresh_metadata:
        update_stocks_metadata()

    if not args.refresh_config and not args.refresh_metadata:
        parser.print_help()

if __name__ == "__main__":
    main()
