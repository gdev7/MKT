import json
import os
from src.data_fetch.metadata_sync import MetadataSync
from src.config import settings

def main():
    config_path = os.path.join(settings.DATA_METADATA_DIR, "indices_config.json")
    
    if not os.path.exists(config_path):
        print(f"Config file not found at {config_path}")
        return

    try:
        with open(config_path, "r") as f:
            indices = json.load(f)
    except Exception as e:
        print(f"Error reading config file: {e}")
        return

    syncer = MetadataSync()
    
    print(f"Found {len(indices)} indices to update.")
    
    for index in indices:
        name = index.get("name")
        url = index.get("url")
        
        if not name or not url:
            print(f"Skipping invalid entry: {index}")
            continue
            
        print(f"Processing index: {name}")
        try:
            syncer.update_index_constituents(name, url)
        except Exception as e:
            print(f"Failed to update index {name}: {e}")

if __name__ == "__main__":
    main()
