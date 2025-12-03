"""
Unified script to update index constituents in metadata.
Can update a single index, multiple indices, or all indices from config.
"""
import sys
import os
import json
import argparse

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.data_fetch.metadata_sync import MetadataSync
from src.config import settings


def update_single_index(sync: MetadataSync, index_name: str, url: str):
    """Update a single index."""
    print(f"Updating {index_name}...")
    try:
        sync.update_index_constituents(index_name, url)
        print(f"✓ Successfully updated {index_name}")
        return True
    except Exception as e:
        print(f"✗ Failed to update {index_name}: {e}")
        return False


def update_all_indices(sync: MetadataSync, config_path: str):
    """Update all indices from config file."""
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return
    
    try:
        with open(config_path, "r") as f:
            indices_config = json.load(f)
    except Exception as e:
        print(f"Error reading config file: {e}")
        return
    
    print(f"Found {len(indices_config)} indices to update.\n")
    
    success_count = 0
    failure_count = 0
    
    for index_info in indices_config:
        name = index_info.get("name")
        url = index_info.get("url")
        
        if name and url:
            print(f"{'-'*60}")
            if update_single_index(sync, name, url):
                success_count += 1
            else:
                failure_count += 1
        else:
            print(f"✗ Skipping invalid index config: {index_info}")
            failure_count += 1
    
    print(f"\n{'-'*60}")
    print(f"Summary:")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {failure_count}")
    print(f"  Total:   {success_count + failure_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Update index constituents in stock metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update all indices from config file
  python update_indices.py --all
  
  # Update a specific index
  python update_indices.py --index "NIFTY 50" --url "https://..."
  
  # Update NIFTY SMALLCAP 100
  python update_indices.py --smallcap
        """
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Update all indices from indices_config.json"
    )
    
    parser.add_argument(
        "--index",
        type=str,
        help="Name of the index to update (requires --url)"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="URL to fetch index data from (requires --index)"
    )
    
    parser.add_argument(
        "--smallcap",
        action="store_true",
        help="Update NIFTY SMALLCAP 100 index"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to indices config file (default: data/metadata/indices_config.json)"
    )
    
    args = parser.parse_args()
    
    # Initialize sync
    sync = MetadataSync()
    
    # Determine config path
    config_path = args.config if args.config else os.path.join(
        settings.DATA_METADATA_DIR, "indices_config.json"
    )
    
    # Handle different modes
    if args.all:
        # Update all indices from config
        update_all_indices(sync, config_path)
    
    elif args.index and args.url:
        # Update a specific index
        update_single_index(sync, args.index, args.url)
    
    elif args.smallcap:
        # Update NIFTY SMALLCAP 100
        url = "https://www.nseindia.com/api/equity-stockIndices?csv=true&index=NIFTY%20SMALLCAP%20100&selectValFormat=crores"
        update_single_index(sync, "NIFTY SMALLCAP 100", url)
    
    else:
        parser.print_help()
        print("\nError: You must specify one of: --all, --index (with --url), or --smallcap")
        sys.exit(1)


if __name__ == "__main__":
    main()
