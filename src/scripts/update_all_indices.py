import sys
import os
import json

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.data_fetch.metadata_sync import MetadataSync
from src.config import settings

def main():
    sync = MetadataSync()
    
    config_path = settings.DATA_METADATA_DIR / "indices_config.json"
    
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        return

    with open(config_path, "r") as f:
        indices_config = json.load(f)
    
    print(f"Found {len(indices_config)} indices to update.")
    
    success_count = 0
    failure_count = 0
    
    for index_info in indices_config:
        name = index_info.get("name")
        url = index_info.get("url")
        
        if name and url:
            print(f"--------------------------------------------------")
            print(f"Processing {name}...")
            try:
                sync.update_index_constituents(name, url)
                success_count += 1
            except Exception as e:
                print(f"FAILED to update {name}: {e}")
                failure_count += 1
        else:
            print(f"Skipping invalid index config: {index_info}")
            failure_count += 1

    print("--------------------------------------------------")
    print(f"All indices processed.")
    print(f"Success: {success_count}")
    print(f"Failed: {failure_count}")

if __name__ == "__main__":
    main()
