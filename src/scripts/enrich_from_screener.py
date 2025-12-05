"""
Enrich metadata from Screener.in with detailed sector classification.

Fetches hierarchical sector data:
- Broad Sector (e.g., Consumer Discretionary)
- Sector Group (e.g., Automobile and Auto Components)
- Sector (e.g., Automobiles)
- Sub-Sector (e.g., 2/3 Wheelers)
"""
import requests
import json
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

# Paths
METADATA_FILE = Path("data/metadata/stocks_metadata.json")
BACKUP_FILE = Path("data/metadata/stocks_metadata_backup_screener.json")

# Screener.in Configuration
SCREENER_BASE_URL = "https://www.screener.in/company"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.screener.in/',
    'Upgrade-Insecure-Requests': '1'
}

# Delay between requests (in seconds) - Heavy delay as requested
REQUEST_DELAY = 3.0  # 3 seconds between requests


class ScreenerEnricher:
    """Enrich stock metadata from Screener.in."""
    
    def __init__(self):
        """Initialize scraper."""
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.success_count = 0
        self.fail_count = 0
        self.skipped_count = 0
        print("✓ Screener.in session initialized")
    
    def fetch_sector_info(self, symbol: str) -> dict:
        """
        Fetch sector information from Screener.in.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with sector information
        """
        try:
            # Build URL - try both consolidated and standalone
            urls = [
                f"{SCREENER_BASE_URL}/{symbol}/consolidated/",
                f"{SCREENER_BASE_URL}/{symbol}/"
            ]
            
            html_content = None
            for url in urls:
                time.sleep(REQUEST_DELAY)  # Heavy delay
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    html_content = response.text
                    break
                elif response.status_code == 404:
                    continue
                else:
                    print(f"    HTTP {response.status_code} for {symbol}")
                    continue
            
            if not html_content:
                return None
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract sector information from the page
            sector_info = {}
            
            # Look for sector hierarchy in <p class="sub"> elements
            # Find all p.sub and look for the one with market links (sector hierarchy)
            all_subs = soup.find_all('p', class_='sub')
            
            for sub_para in all_subs:
                # Look for links with /market/ in href (sector hierarchy)
                sector_links = sub_para.find_all('a', href=re.compile(r'/market/'))
                
                if sector_links and len(sector_links) >= 1:
                    # Extract text from each link
                    # The hierarchy is: Broad Sector -> Sector -> Broad Industry -> Industry
                    sectors = [link.get_text(strip=True) for link in sector_links]
                    
                    # Map to our schema based on titles or count
                    # Screener.in uses 4 levels in their classification
                    if len(sectors) >= 1:
                        sector_info['BROAD_SECTOR'] = sectors[0]
                    if len(sectors) >= 2:
                        sector_info['SECTOR_GROUP'] = sectors[1]
                    if len(sectors) >= 3:
                        sector_info['SECTOR'] = sectors[2]
                    if len(sectors) >= 4:
                        sector_info['SUB_SECTOR'] = sectors[3]
                    
                    break  # Found the sector paragraph, no need to continue
            
            # Add timestamp
            if sector_info:
                sector_info['LAST_UPDATED'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return sector_info
            
            return None
            
        except requests.exceptions.Timeout:
            print(f"    Timeout for {symbol}")
            return None
        except Exception as e:
            print(f"    Error for {symbol}: {e}")
            return None
    
    def enrich_metadata(self, limit: int = None, resume_from: str = None):
        """
        Enrich all stocks in metadata file.
        
        Args:
            limit: If set, only process first N stocks
            resume_from: Symbol to resume from (for interrupted runs)
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
        
        # Resume support
        if resume_from:
            if resume_from in symbols:
                resume_idx = symbols.index(resume_from)
                symbols = symbols[resume_idx:]
                print(f"Resuming from {resume_from} ({len(symbols)} stocks remaining)")
            else:
                print(f"Resume symbol {resume_from} not found, starting from beginning")
        
        if limit:
            symbols = symbols[:limit]
            print(f"Processing first {limit} stocks (test mode)")
        
        print(f"\nEnriching {len(symbols)} stocks from Screener.in...")
        print(f"Delay: {REQUEST_DELAY} seconds between requests")
        print(f"Estimated time: {len(symbols) * REQUEST_DELAY / 60:.1f} minutes\n")
        
        # Process each stock
        for idx, symbol in enumerate(tqdm(symbols, desc="Enriching"), 1):
            print(f"\r[{idx}/{len(symbols)}] {symbol:15} ", end="", flush=True)
            sector_info = self.fetch_sector_info(symbol)
            
            if sector_info:
                # Update metadata with hierarchical sectors
                metadata[symbol]['BROAD_SECTOR'] = sector_info.get('BROAD_SECTOR', '')
                metadata[symbol]['SECTOR_GROUP'] = sector_info.get('SECTOR_GROUP', '')
                metadata[symbol]['SECTOR'] = sector_info.get('SECTOR', '')
                metadata[symbol]['SUB_SECTOR'] = sector_info.get('SUB_SECTOR', '')
                metadata[symbol]['LAST_UPDATED'] = sector_info.get('LAST_UPDATED', '')
                self.success_count += 1
                print(f"✓ {sector_info.get('BROAD_SECTOR', '')[:20]:20} → {sector_info.get('SUB_SECTOR', '')[:30]}")
            else:
                self.fail_count += 1
                print(f"✗ FAILED TO FETCH DATA")
            
            # Save after EVERY stock update to avoid losing progress
            with open(METADATA_FILE, 'w') as f:
                json.dump(metadata, f, indent=4)
            
            # Progress summary every 50 stocks
            if idx % 50 == 0:
                elapsed = idx * REQUEST_DELAY / 60
                remaining = (len(symbols) - idx) * REQUEST_DELAY / 60
                print(f"\n{'='*60}")
                print(f"  Progress: {idx}/{len(symbols)} stocks ({idx/len(symbols)*100:.1f}%)")
                print(f"  Success: {self.success_count} | Failed: {self.fail_count}")
                print(f"  Time elapsed: {elapsed:.1f} min | Remaining: {remaining:.1f} min")
                print(f"{'='*60}\n")
        
        # Final save
        print(f"\nSaving final enriched metadata to {METADATA_FILE}...")
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        # Summary
        print("\n" + "="*60)
        print("ENRICHMENT SUMMARY")
        print("="*60)
        print(f"Total stocks processed:    {len(symbols)}")
        print(f"Successfully enriched:     {self.success_count}")
        print(f"Failed:                    {self.fail_count}")
        print(f"Success rate:              {self.success_count/len(symbols)*100:.1f}%")
        print(f"\nBackup saved at: {BACKUP_FILE}")
        print("="*60)


def main():
    """Main execution function."""
    import argparse
    print("1")
    parser = argparse.ArgumentParser(description="Enrich stock metadata from Screener.in")
    parser.add_argument('--limit', type=int, help='Limit number of stocks (for testing)')
    parser.add_argument('--test', action='store_true', help='Test mode: only process 5 stocks')
    parser.add_argument('--resume', type=str, help='Resume from this symbol')
    args = parser.parse_args()
    
    limit = args.limit
    if args.test:
        limit = 5

    print("2")
    
    print("="*60)
    print("SCREENER.IN METADATA ENRICHMENT")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Source: Screener.in")
    print(f"Delay: {REQUEST_DELAY} seconds between requests")
    if limit:
        print(f"Mode: TEST (limit={limit})")
    elif args.resume:
        print(f"Mode: RESUME from {args.resume}")
    else:
        print(f"Mode: FULL")
    print("="*60)
    
    enricher = ScreenerEnricher()
    enricher.enrich_metadata(limit=limit, resume_from=args.resume)


if __name__ == "__main__":
    main()
