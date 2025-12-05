"""
Enhanced metadata enrichment script - fetches additional fields from NSE.

This script enriches the existing stocks_metadata.json with:
- SECTOR
- INDUSTRY  
- LAST_UPDATED

Uses NSE Official API only for consistency.
"""
import requests
import json
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# Paths
METADATA_FILE = Path("data/metadata/stocks_metadata.json")
BACKUP_FILE = Path("data/metadata/stocks_metadata_backup.json")

# NSE API Configuration
NSE_BASE_URL = "https://www.nseindia.com"
NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nseindia.com/',
}

class NSEMetadataEnricher:
    """Enriches stock metadata using NSE Official API."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(NSE_HEADERS)
        self._initialize_session()
        
    def _initialize_session(self):
        """Initialize session by visiting NSE homepage to get cookies."""
        try:
            response = self.session.get(NSE_BASE_URL, timeout=10)
            if response.status_code == 200:
                print("✓ NSE session initialized")
                return True
            else:
                print(f"⚠ NSE returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Failed to initialize NSE session: {e}")
            return False
    
    def fetch_stock_info(self, symbol):
        """
        Fetch detailed stock information from NSE.
        
        API: /api/quote-equity?symbol=SYMBOL
        Returns: Sector, Industry, Status, and other metadata
        """
        url = f"{NSE_BASE_URL}/api/quote-equity"
        params = {'symbol': symbol}
        
        try:
            time.sleep(0.5)  # Rate limiting
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant fields
                info = data.get('info', {})
                metadata = data.get('metadata', {})
                
                enriched_data = {
                    'SECTOR': info.get('sector', ''),
                    'INDUSTRY': info.get('industry', ''),
                    'LAST_UPDATED': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Additional fields if available
                if metadata:
                    enriched_data['SERIES_FULL'] = metadata.get('series', '')
                
                return enriched_data
            else:
                return None
                
        except Exception as e:
            print(f"    Error fetching {symbol}: {e}")
            return None
    
    def enrich_metadata(self, limit=None):
        """
        Enrich all stocks in metadata file.
        
        Args:
            limit: If set, only process first N stocks (for testing)
        """
        # Load existing metadata
        print(f"\nLoading metadata from {METADATA_FILE}...")
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        
        total_stocks = len(metadata)
        print(f"Found {total_stocks} stocks in metadata")
        
        # Create backup
        print(f"Creating backup at {BACKUP_FILE}...")
        with open(BACKUP_FILE, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        # Process stocks
        symbols = list(metadata.keys())
        if limit:
            symbols = symbols[:limit]
            print(f"Processing first {limit} stocks (test mode)")
        
        print(f"\nEnriching {len(symbols)} stocks from NSE...\n")
        
        success_count = 0
        fail_count = 0
        
        for symbol in tqdm(symbols, desc="Enriching"):
            enriched_data = self.fetch_stock_info(symbol)
            
            if enriched_data:
                # Merge with existing data
                metadata[symbol].update(enriched_data)
                success_count += 1
            else:
                fail_count += 1
                # Still update timestamp even if fetch failed
                metadata[symbol]['LAST_UPDATED'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                metadata[symbol]['ENRICHMENT_STATUS'] = 'Failed'
        
        # Save enriched metadata
        print(f"\nSaving enriched metadata to {METADATA_FILE}...")
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        # Summary
        print("\n" + "="*60)
        print("ENRICHMENT SUMMARY")
        print("="*60)
        print(f"Total stocks:     {len(symbols)}")
        print(f"Successfully enriched: {success_count}")
        print(f"Failed:           {fail_count}")
        print(f"Success rate:     {success_count/len(symbols)*100:.1f}%")
        print("\nBackup saved at:", BACKUP_FILE)
        print("="*60)
        
        return metadata


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enrich stock metadata from NSE")
    parser.add_argument('--limit', type=int, help='Limit number of stocks (for testing)')
    parser.add_argument('--test', action='store_true', help='Test mode: only process 10 stocks')
    args = parser.parse_args()
    
    limit = args.limit
    if args.test:
        limit = 10
    
    print("="*60)
    print("NSE METADATA ENRICHMENT")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Source: NSE Official API")
    if limit:
        print(f"Mode: TEST (limit={limit})")
    else:
        print(f"Mode: FULL")
    print("="*60)
    
    enricher = NSEMetadataEnricher()
    enricher.enrich_metadata(limit=limit)


if __name__ == "__main__":
    main()
