"""
Stock Metadata Enrichment - Screener.in Data Source

Enriches stock metadata with comprehensive fundamental data:
1. Sector classification (4-level hierarchy)
2. Financial ratios (Market Cap, P/E, ROE, ROCE, etc.)
3. Company identifiers (Website, BSE/NSE codes)
4. Price metrics (Current price, 52-week high/low)
5. Fundamental metrics (Book Value, Dividend Yield, Face Value)
6. Shareholding patterns (quarterly)
7. Quarterly results (13 quarters)
8. Growth metrics (Sales/Profit growth)

Usage:
    python src/scripts/enrich_stocks.py [OPTIONS]
    
Options:
    --limit N                    Process first N stocks
    --test                       Test mode (5 stocks)
    --resume SYMBOL              Resume from specific stock
    --index "INDEX NAME"         Enrich specific index stocks
    --market-cap-min VALUE       Minimum market cap filter (Cr)
    --market-cap-max VALUE       Maximum market cap filter (Cr)
    --filter-enriched            Skip already enriched stocks

Examples:
    python src/scripts/enrich_stocks.py --index "NIFTY 50"
    python src/scripts/enrich_stocks.py --market-cap-min 1000 --market-cap-max 10000
    python src/scripts/enrich_stocks.py --filter-enriched --limit 100
"""
import requests
import json
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import sys
import os

# Paths
METADATA_FILE = Path("data/metadata/stocks_metadata.json")
BACKUP_FILE = Path("data/metadata/stocks_metadata_backup.json")

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

# Delay between requests (in seconds)
REQUEST_DELAY = 3.0


class ScreenerEnricher:
    """Enrich stock metadata with comprehensive data from Screener.in."""
    
    def __init__(self):
        """Initialize scraper."""
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.success_count = 0
        self.fail_count = 0
    
    def extract_number(self, text: str) -> str:
        """Extract numeric value from text, handling Cr, Lakhs, etc."""
        if not text:
            return ''
        
        # Remove commas and whitespace
        text = text.replace(',', '').strip()
        
        # Keep the text as-is with units (Cr, Lakhs, etc.)
        return text
    
    def fetch_from_nse(self, symbol: str) -> dict:
        """
        Fetch basic data from NSE as fallback.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with NSE data
        """
        info = {}
        
        try:
            nse_session = requests.Session()
            nse_session.headers.update({
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
            })
            
            # Get main page first for cookies
            nse_session.get('https://www.nseindia.com', timeout=10)
            time.sleep(1)
            
            # Get quote data
            url = f'https://www.nseindia.com/api/quote-equity?symbol={symbol}'
            response = nse_session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract available data
                priceInfo = data.get('priceInfo', {})
                company_info = data.get('info', {})
                
                if priceInfo.get('lastPrice'):
                    info['CURRENT_PRICE'] = str(priceInfo['lastPrice'])
                
                if company_info.get('companyName'):
                    info['DESCRIPTION'] = company_info['companyName']
                
                if company_info.get('industry'):
                    info['SECTOR'] = company_info['industry']
                
        except Exception as e:
            pass
        
        return info
    
    def fetch_complete_info(self, symbol: str) -> dict:
        """
        Fetch complete information from Screener.in.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with all available information
        """
        try:
            # Build URL - try both consolidated and standalone
            urls = [
                f"{SCREENER_BASE_URL}/{symbol}/consolidated/",
                f"{SCREENER_BASE_URL}/{symbol}/"
            ]
            
            soup = None
            for url in urls:
                time.sleep(REQUEST_DELAY)
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    temp_soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check if this page has valid ratio data
                    # For banks/financial companies, consolidated pages often have empty values
                    ratios_div = temp_soup.find('div', class_='company-ratios')
                    if ratios_div:
                        # Check if at least one number span has content
                        has_data = False
                        for num_span in ratios_div.find_all('span', class_='number'):
                            if num_span.get_text(strip=True):
                                has_data = True
                                break
                        
                        if has_data:
                            soup = temp_soup
                            break
                        # If no data, try next URL (standalone)
                    else:
                        # No ratios div, try next URL
                        continue
                elif response.status_code == 404:
                    continue
                else:
                    continue
            
            if not soup:
                return None
            
            info = {}
            
            # 1. SECTOR CLASSIFICATION (4-level hierarchy)
            all_subs = soup.find_all('p', class_='sub')
            for sub_para in all_subs:
                sector_links = sub_para.find_all('a', href=re.compile(r'/market/'))
                
                if sector_links and len(sector_links) >= 1:
                    sectors = [link.get_text(strip=True) for link in sector_links]
                    
                    if len(sectors) >= 1:
                        info['BROAD_SECTOR'] = sectors[0]
                    if len(sectors) >= 2:
                        info['SECTOR_GROUP'] = sectors[1]
                    if len(sectors) >= 3:
                        info['SECTOR'] = sectors[2]
                    if len(sectors) >= 4:
                        info['SUB_SECTOR'] = sectors[3]
                    
                    break
            
            # 2. KEY FINANCIAL RATIOS
            ratios_section = soup.find('div', class_='company-ratios')
            if ratios_section:
                for item in ratios_section.find_all('li'):
                    name_span = item.find('span', class_='name')
                    number_span = item.find('span', class_='number')
                    
                    if name_span and number_span:
                        name = name_span.get_text(strip=True)
                        value = self.extract_number(number_span.get_text(strip=True))
                        
                        # Map to our field names
                        field_map = {
                            'Market Cap': 'MARKET_CAP',
                            'Current Price': 'CURRENT_PRICE',
                            'High / Low': 'HIGH_LOW_52W',
                            'Stock P/E': 'PE_RATIO',
                            'Book Value': 'BOOK_VALUE',
                            'Dividend Yield': 'DIVIDEND_YIELD',
                            'ROCE': 'ROCE',
                            'ROE': 'ROE',
                            'Face Value': 'FACE_VALUE'
                        }
                        
                        if name in field_map:
                            info[field_map[name]] = value
            
            # 3. COMPANY IDENTIFIERS
            company_links = soup.find('div', class_='company-links')
            if company_links:
                for link in company_links.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Website
                    if 'http' in href and 'bseindia' not in href and 'nseindia' not in href:
                        info['WEBSITE'] = href
                    
                    # BSE Code
                    if 'bseindia' in href:
                        # Extract BSE code from text or URL
                        bse_match = re.search(r'(\d{6,})', text + href)
                        if bse_match:
                            info['BSE_CODE'] = bse_match.group(1)
                    
                    # NSE Symbol already known, but store for consistency
                    if 'nseindia' in href:
                        info['NSE_SYMBOL'] = symbol
            
            # 4. COMPANY DESCRIPTION
            about_section = soup.find('div', class_='company-info')
            if about_section:
                # Get the About text
                about_p = about_section.find('p')
                if about_p:
                    description = about_p.get_text(strip=True)
                    # Limit to reasonable length
                    if len(description) > 500:
                        description = description[:497] + '...'
                    info['DESCRIPTION'] = description
            
            # 5. Growth Metrics - Compounded Sales and Profit Growth
            # Find all tables and look for growth metrics
            for table in soup.find_all('table'):
                table_text = table.get_text()
                
                # Compounded Sales Growth
                if 'Compounded Sales Growth' in table_text:
                    for row in table.find_all('tr'):
                        cells = row.find_all(['th', 'td'])
                        if len(cells) == 2:
                            period = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            
                            if period == '3 Years:':
                                info['SALES_GROWTH_3Y'] = value
                            elif period == '5 Years:':
                                info['SALES_GROWTH_5Y'] = value
                            elif period == 'TTM:':
                                info['SALES_GROWTH_TTM'] = value
                
                # Compounded Profit Growth
                if 'Compounded Profit Growth' in table_text:
                    for row in table.find_all('tr'):
                        cells = row.find_all(['th', 'td'])
                        if len(cells) == 2:
                            period = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            
                            if period == '3 Years:':
                                info['PROFIT_GROWTH_3Y'] = value
                            elif period == '5 Years:':
                                info['PROFIT_GROWTH_5Y'] = value
                            elif period == 'TTM:':
                                info['PROFIT_GROWTH_TTM'] = value
                
                # Operating Profit Margin (OPM) trends
                if 'OPM' in table_text and 'Mar' in table_text:
                    # Get latest OPM from annual data
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['th', 'td'])
                        if cells and 'OPM' in cells[0].get_text():
                            # Get most recent value (usually last column)
                            if len(cells) > 1:
                                latest_opm = cells[-1].get_text(strip=True)
                                if latest_opm and latest_opm != '-':
                                    info['OPM_LATEST'] = latest_opm
                                    break
            
            # 6. Debt to Equity - from Balance Sheet
            balance_sheet = soup.find('section', id='balance-sheet')
            if balance_sheet:
                table = balance_sheet.find('table')
                if table:
                    # Find Borrowings row
                    borrowings_val = None
                    equity_val = None
                    
                    for row in table.find_all('tr'):
                        cells = row.find_all(['th', 'td'])
                        if cells:
                            first_cell = cells[0].get_text(strip=True).lower()
                            
                            # Get latest borrowings (last column)
                            if 'borrowing' in first_cell and len(cells) > 1:
                                borrowings_val = cells[-1].get_text(strip=True).replace(',', '')
                            
                            # Get latest equity/shareholders funds
                            if ('equity capital' in first_cell or 'reserves' in first_cell) and len(cells) > 1:
                                equity_val = cells[-1].get_text(strip=True).replace(',', '')
                    
                    # Calculate Debt to Equity if both values found
                    if borrowings_val and equity_val:
                        try:
                            debt = float(borrowings_val)
                            equity = float(equity_val)
                            if equity != 0:
                                debt_to_equity = round(debt / equity, 2)
                                info['DEBT_TO_EQUITY'] = str(debt_to_equity)
                        except:
                            pass
            
            # 6. SHAREHOLDING PATTERN - Quarterly Time Series Data
            shareholders_section = soup.find('section', id='shareholding')
            if shareholders_section:
                # Find the shareholding table
                table = shareholders_section.find('table')
                if table:
                    shareholding_data = []
                    
                    # Get headers (quarters)
                    headers = []
                    header_row = table.find('thead')
                    if header_row:
                        for th in header_row.find_all('th'):
                            quarter = th.get_text(strip=True)
                            if quarter and quarter != 'Shareholding Pattern':
                                headers.append(quarter)
                    
                    # Get rows (Promoters, FII, DII, Public)
                    tbody = table.find('tbody')
                    if tbody and headers:
                        for row in tbody.find_all('tr'):
                            cells = row.find_all('td')
                            if cells:
                                shareholder_type = cells[0].get_text(strip=True)
                                
                                # Extract values for each quarter
                                for i, quarter in enumerate(headers):
                                    if i + 1 < len(cells):
                                        value = cells[i + 1].get_text(strip=True).replace('%', '').strip()
                                        
                                        shareholding_data.append({
                                            'quarter': quarter,
                                            'type': shareholder_type,
                                            'percentage': value
                                        })
                    
                    if shareholding_data:
                        # Store as time-series data, not in HISTORY
                        info['SHAREHOLDING_PATTERN'] = shareholding_data
            
            # 7. QUARTERLY RESULTS - Time Series Data
            quarters_section = soup.find('section', id='quarters')
            if quarters_section:
                table = quarters_section.find('table')
                if table:
                    quarterly_data = []
                    
                    # Get quarter headers
                    headers = []
                    header_row = table.find('thead')
                    if header_row:
                        for th in header_row.find_all('th'):
                            quarter = th.get_text(strip=True)
                            if quarter and quarter not in ['', 'Quarterly Results']:
                                headers.append(quarter)
                    
                    # Get financial metrics
                    tbody = table.find('tbody')
                    if tbody and headers:
                        # Create dict for each quarter
                        quarter_dicts = {q: {'quarter': q} for q in headers}
                        
                        for row in tbody.find_all('tr'):
                            cells = row.find_all('td')
                            if cells:
                                metric_name = cells[0].get_text(strip=True)
                                
                                # Map metric names
                                metric_map = {
                                    'Sales': 'sales',
                                    'Expenses': 'expenses',
                                    'Operating Profit': 'operating_profit',
                                    'OPM %': 'opm',
                                    'Other Income': 'other_income',
                                    'Interest': 'interest',
                                    'Depreciation': 'depreciation',
                                    'Profit before tax': 'profit_before_tax',
                                    'Tax %': 'tax_rate',
                                    'Net Profit': 'net_profit',
                                    'NPM %': 'npm',
                                    'EPS in Rs': 'eps'
                                }
                                
                                if metric_name in metric_map:
                                    field_name = metric_map[metric_name]
                                    
                                    for i, quarter in enumerate(headers):
                                        if i + 1 < len(cells):
                                            value = cells[i + 1].get_text(strip=True)
                                            quarter_dicts[quarter][field_name] = value
                        
                        quarterly_data = list(quarter_dicts.values())
                    
                    if quarterly_data:
                        info['QUARTERLY_RESULTS'] = quarterly_data
            
            # Add timestamp
            if info:
                info['LAST_UPDATED'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # FALLBACK: If critical fields are missing, try NSE
                if not info.get('MARKET_CAP') or not info.get('CURRENT_PRICE'):
                    nse_data = self.fetch_from_nse(symbol)
                    # Only fill in missing fields, don't override existing ones
                    for key, value in nse_data.items():
                        if key not in info or not info.get(key) or info[key] == '':
                            info[key] = value
                
                return info
            
            return None
            
        except requests.exceptions.Timeout:
            return None
        except Exception as e:
            return None
    
    def calculate_change(self, old_value: str, new_value: str) -> dict:
        """
        Calculate percentage change between old and new values.
        
        Args:
            old_value: Previous value (may contain units like Cr, %)
            new_value: New value (may contain units)
        
        Returns:
            Dict with absolute and percentage change
        """
        try:
            # Extract numeric part
            old_num = float(re.sub(r'[^\d.-]', '', old_value.replace(',', '')))
            new_num = float(re.sub(r'[^\d.-]', '', new_value.replace(',', '')))
            
            change = new_num - old_num
            pct_change = (change / old_num * 100) if old_num != 0 else 0
            
            return {
                'change': round(change, 2),
                'pct_change': round(pct_change, 2)
            }
        except:
            return {'change': 0, 'pct_change': 0}
    
    def enrich_metadata(self, limit: int = None, resume_from: str = None, symbols_list: list = None):
        """
        Enrich all stocks in metadata file with historical tracking.
        
        Args:
            limit: If set, only process first N stocks
            resume_from: Symbol to resume from (for interrupted runs)
            symbols_list: Specific list of symbols to enrich (overrides other options)
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
        if symbols_list:
            # Use provided symbols list
            symbols = [s for s in symbols_list if s in metadata]
            print(f"Enriching {len(symbols)} filtered stocks")
        else:
            # Use all symbols or resume
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
            stock_info = self.fetch_complete_info(symbol)
            
            if stock_info:
                # Track historical changes for SINGLE-VALUE dynamic fields
                dynamic_fields = ['MARKET_CAP', 'CURRENT_PRICE', 'PE_RATIO', 'ROCE', 'ROE', 
                                'BOOK_VALUE', 'DIVIDEND_YIELD', 'HIGH_LOW_52W']
                
                # TIME-SERIES fields (stored as arrays, not tracked in HISTORY)
                timeseries_fields = ['SHAREHOLDING_PATTERN', 'QUARTERLY_RESULTS']
                
                # Initialize history dict if not exists
                if 'HISTORY' not in metadata[symbol]:
                    metadata[symbol]['HISTORY'] = {}
                
                current_time = datetime.now().strftime('%Y-%m-%d')
                
                # Track changes for each SINGLE-VALUE dynamic field
                for field in dynamic_fields:
                    if field in stock_info:
                        new_value = stock_info[field]
                        old_value = metadata[symbol].get(field)
                        
                        # If field exists and value changed, track it
                        if old_value and old_value != new_value:
                            if field not in metadata[symbol]['HISTORY']:
                                metadata[symbol]['HISTORY'][field] = []
                            
                            # Calculate change
                            change_info = self.calculate_change(old_value, new_value)
                            
                            # Store historical record
                            history_entry = {
                                'date': current_time,
                                'old_value': old_value,
                                'new_value': new_value,
                                'change': change_info['change'],
                                'pct_change': change_info['pct_change']
                            }
                            
                            metadata[symbol]['HISTORY'][field].append(history_entry)
                            
                            # Keep only last 20 historical records per field
                            if len(metadata[symbol]['HISTORY'][field]) > 20:
                                metadata[symbol]['HISTORY'][field] = metadata[symbol]['HISTORY'][field][-20:]
                
                # Handle TIME-SERIES fields - Replace entirely, don't track changes
                for field in timeseries_fields:
                    if field in stock_info:
                        # Just update the entire time-series array
                        metadata[symbol][field] = stock_info[field]
                
                # Update metadata with all fetched information
                # Skip empty values to avoid storing blank data
                for key, value in stock_info.items():
                    if value and str(value).strip():  # Only store non-empty values
                        metadata[symbol][key] = value
                
                self.success_count += 1
                sector = stock_info.get('BROAD_SECTOR', 'N/A')[:20]
                mkt_cap = stock_info.get('MARKET_CAP', 'N/A')
                
                # Show if values changed or time-series data collected
                changes_count = len([f for f in dynamic_fields if f in metadata[symbol].get('HISTORY', {})])
                timeseries_count = len([f for f in timeseries_fields if f in stock_info])
                
                indicators = []
                if changes_count > 0:
                    indicators.append(f"{changes_count} changed")
                if timeseries_count > 0:
                    indicators.append(f"{timeseries_count} TS")
                
                indicator_str = f" ({', '.join(indicators)})" if indicators else ""
                print(f"✓ {sector:20} | Cap: {mkt_cap:12}{indicator_str}")
            else:
                self.fail_count += 1
                print(f"✗ FAILED TO FETCH DATA")
            
            # Save after EVERY stock update
            with open(METADATA_FILE, 'w') as f:
                json.dump(metadata, f, indent=4)
            
            # Progress summary every 50 stocks
            if idx % 50 == 0:
                elapsed = idx * REQUEST_DELAY / 60
                remaining = (len(symbols) - idx) * REQUEST_DELAY / 60
                print(f"\n{'='*70}")
                print(f"  Progress: {idx}/{len(symbols)} stocks ({idx/len(symbols)*100:.1f}%)")
                print(f"  Success: {self.success_count} | Failed: {self.fail_count}")
                print(f"  Time elapsed: {elapsed:.1f} min | Remaining: {remaining:.1f} min")
                print(f"{'='*70}\n")
        
        # Final save
        print(f"\nSaving final enriched metadata to {METADATA_FILE}...")
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        # Summary
        print("\n" + "="*70)
        print("ENRICHMENT SUMMARY")
        print("="*70)
        print(f"Total stocks processed:    {len(symbols)}")
        print(f"Successfully enriched:     {self.success_count}")
        print(f"Failed:                    {self.fail_count}")
        print(f"Success rate:              {self.success_count/len(symbols)*100:.1f}%")
        print(f"\nBackup saved at: {BACKUP_FILE}")
        print("="*70)


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete enrichment from Screener.in")
    parser.add_argument('--limit', type=int, help='Limit number of stocks (for testing)')
    parser.add_argument('--test', action='store_true', help='Test mode: only process 5 stocks')
    parser.add_argument('--resume', type=str, help='Resume from this symbol')
    parser.add_argument('--index', type=str, help='Enrich stocks from specific index (e.g., "NIFTY SMALLCAP 100")')
    parser.add_argument('--market-cap-min', type=float, help='Minimum market cap (in Cr)')
    parser.add_argument('--market-cap-max', type=float, help='Maximum market cap (in Cr)')
    parser.add_argument('--filter-enriched', action='store_true', help='Only enrich stocks that are not already enriched')
    
    args = parser.parse_args()
    
    limit = args.limit
    if args.test:
        limit = 5
    
    # Load metadata to apply filters
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    
    # Apply filters to get symbols to enrich
    symbols_to_enrich = []
    filter_info = []
    
    # Filter by index
    if args.index:
        for symbol, stock in metadata.items():
            if args.index in stock.get('INDICES', []):
                symbols_to_enrich.append(symbol)
        filter_info.append(f"Index: {args.index}")
    
    # Filter by market cap range
    elif args.market_cap_min is not None or args.market_cap_max is not None:
        for symbol, stock in metadata.items():
            market_cap = stock.get('MARKET_CAP')
            if market_cap:
                try:
                    # Remove commas and convert to float
                    cap_value = float(str(market_cap).replace(',', ''))
                    
                    # Apply filters
                    if args.market_cap_min is not None and cap_value < args.market_cap_min:
                        continue
                    if args.market_cap_max is not None and cap_value > args.market_cap_max:
                        continue
                    
                    symbols_to_enrich.append(symbol)
                except:
                    pass
        
        if args.market_cap_min and args.market_cap_max:
            filter_info.append(f"Market Cap: {args.market_cap_min}-{args.market_cap_max} Cr")
        elif args.market_cap_min:
            filter_info.append(f"Market Cap: >{args.market_cap_min} Cr")
        elif args.market_cap_max:
            filter_info.append(f"Market Cap: <{args.market_cap_max} Cr")
    
    # Filter out already enriched stocks
    if args.filter_enriched and symbols_to_enrich:
        original_count = len(symbols_to_enrich)
        symbols_to_enrich = [s for s in symbols_to_enrich if 'MARKET_CAP' not in metadata.get(s, {})]
        filtered_count = original_count - len(symbols_to_enrich)
        filter_info.append(f"Filtered {filtered_count} already enriched")
    
    print("="*70)
    print("STOCK METADATA ENRICHMENT")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Source: Screener.in")
    print(f"Delay: {REQUEST_DELAY} seconds between requests")
    
    if symbols_to_enrich:
        print(f"Mode: FILTERED ({len(symbols_to_enrich)} stocks)")
        for info in filter_info:
            print(f"  {info}")
    elif limit:
        print(f"Mode: TEST (limit={limit})")
    elif args.resume:
        print(f"Mode: RESUME from {args.resume}")
    else:
        print(f"Mode: FULL")
    
    print("\nData to be collected:")
    print("  • 4-level sector classification")
    print("  • Market Cap, P/E, ROE, ROCE")
    print("  • Current Price, 52-week High/Low")
    print("  • Book Value, Dividend Yield, Face Value")
    print("  • Company identifiers (Website, BSE/NSE codes)")
    print("  • Company description")
    print("  • Additional ratios (Debt/Equity, Growth metrics)")
    print("  • Shareholding pattern (quarterly)")
    print("="*70)
    
    enricher = ScreenerEnricher()
    
    # Use filtered symbols if available
    if symbols_to_enrich:
        enricher.enrich_metadata(limit=limit, resume_from=None, symbols_list=symbols_to_enrich)
    else:
        enricher.enrich_metadata(limit=limit, resume_from=args.resume)


if __name__ == "__main__":
    main()
