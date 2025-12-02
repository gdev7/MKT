import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.data_fetch.metadata_sync import MetadataSync

def main():
    sync = MetadataSync()
    
    # URL provided by the user
    url = "https://www.nseindia.com/api/equity-stockIndices?csv=true&index=NIFTY%20SMALLCAP%20100&selectValFormat=crores"
    index_name = "NIFTY SMALLCAP 100"
    
    print(f"Updating metadata with {index_name} constituents...")
    sync.update_index_constituents(index_name, url)
    print("Done.")

if __name__ == "__main__":
    main()
