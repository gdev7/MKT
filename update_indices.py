import json
import requests
import csv
import os
import time

def update_metadata():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "data", "metadata", "indices_config.json")
    metadata_path = os.path.join(base_dir, "data", "metadata", "stocks_metadata.json")
    
    print(f"Reading config from: {config_path}")
    if not os.path.exists(config_path):
        print("Config file not found!")
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

    # Setup session
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.nseindia.com/'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
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

if __name__ == "__main__":
    update_metadata()
