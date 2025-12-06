"""
Data Reader - Unified interface for loading all data types

Provides centralized data access for:
- Stock price data (OHLCV from CSV files)
- Enriched metadata (sectors, ratios, financials)
- Index memberships
- Candlestick patterns
- Any other data sources

Usage:
    from src.utils.data_reader import DataReader
    
    reader = DataReader()
    
    # Load price data
    df = reader.get_price_data('HDFCBANK')
    
    # Load metadata
    metadata = reader.get_stock_metadata('HDFCBANK')
    
    # Load all metadata
    all_stocks = reader.get_all_metadata()
    
    # Get stocks by index
    nifty50 = reader.get_stocks_by_index('NIFTY 50')
"""

import pandas as pd
import json
from pathlib import Path
from typing import Optional, Dict, List, Union, Any
from datetime import datetime, timedelta


class DataReader:
    """
    Unified data reader for all stock market data sources.
    
    Handles:
    - Price data (OHLCV) from CSV files
    - Enriched metadata (JSON)
    - Index configurations
    - Filtering and querying
    """
    
    def __init__(self, 
                 data_dir: str = "data",
                 raw_dir: str = "data/raw",
                 metadata_file: str = "data/metadata/stocks_metadata.json",
                 indices_config: str = "data/metadata/indices_config.json"):
        """
        Initialize data reader.
        
        Args:
            data_dir: Base data directory
            raw_dir: Directory containing price CSV files
            metadata_file: Path to stocks metadata JSON
            indices_config: Path to indices configuration
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = Path(raw_dir)
        self.metadata_file = Path(metadata_file)
        self.indices_config_file = Path(indices_config)
        
        # Cache for frequently accessed data
        self._metadata_cache = None
        self._indices_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 300  # Cache for 5 minutes
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache_timestamp is None:
            return False
        return (datetime.now() - self._cache_timestamp).seconds < self._cache_ttl
    
    def _load_metadata(self, force_reload: bool = False) -> Dict:
        """
        Load metadata from JSON file with caching.
        
        Args:
            force_reload: Force reload even if cache is valid
            
        Returns:
            Dictionary of stock metadata
        """
        if not force_reload and self._is_cache_valid() and self._metadata_cache:
            return self._metadata_cache
        
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r') as f:
                self._metadata_cache = json.load(f)
                self._cache_timestamp = datetime.now()
                return self._metadata_cache
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return {}
    
    def _load_indices_config(self) -> Dict:
        """Load indices configuration."""
        if self._indices_cache is not None:
            return self._indices_cache
        
        if not self.indices_config_file.exists():
            return {}
        
        try:
            with open(self.indices_config_file, 'r') as f:
                self._indices_cache = json.load(f)
                return self._indices_cache
        except Exception as e:
            print(f"Error loading indices config: {e}")
            return {}
    
    # ==================== PRICE DATA ====================
    
    def get_price_data(self, symbol: str, 
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load price data (OHLCV) for a stock.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD) or None for all data
            end_date: End date (YYYY-MM-DD) or None for all data
            
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
            or None if data not found
        """
        file_path = self.raw_dir / f"{symbol}.csv"
        
        if not file_path.exists():
            return None
        
        try:
            # Read CSV, skip first 2 rows (headers)
            df = pd.read_csv(file_path, skiprows=2)
            
            # Rename columns
            df.columns = ['date', 'close', 'high', 'low', 'open', 'volume']
            
            # Remove rows with missing dates
            df = df[df['date'].notna() & (df['date'] != '')]
            
            # Convert to proper types
            df['date'] = pd.to_datetime(df['date'])
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            # Remove rows with NaN in OHLC
            df = df.dropna(subset=['open', 'high', 'low', 'close'])
            
            # Sort by date
            df = df.sort_values('date')
            df.reset_index(drop=True, inplace=True)
            
            # Filter by date range if provided
            if start_date:
                start = pd.to_datetime(start_date)
                df = df[df['date'] >= start]
            
            if end_date:
                end = pd.to_datetime(end_date)
                df = df[df['date'] <= end]
            
            return df
            
        except Exception as e:
            print(f"Error loading price data for {symbol}: {e}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the most recent closing price.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Latest close price or None
        """
        df = self.get_price_data(symbol)
        if df is None or len(df) == 0:
            return None
        return float(df.iloc[-1]['close'])
    
    def get_price_range(self, symbol: str, days: int = 30) -> Optional[Dict]:
        """
        Get price statistics for recent period.
        
        Args:
            symbol: Stock symbol
            days: Number of days to analyze
            
        Returns:
            Dict with high, low, avg, current, change_pct
        """
        df = self.get_price_data(symbol)
        if df is None or len(df) == 0:
            return None
        
        recent = df.tail(days)
        current = float(recent.iloc[-1]['close'])
        start_price = float(recent.iloc[0]['close'])
        
        return {
            'high': float(recent['high'].max()),
            'low': float(recent['low'].min()),
            'avg': float(recent['close'].mean()),
            'current': current,
            'change_pct': ((current - start_price) / start_price * 100) if start_price > 0 else 0,
            'days': len(recent)
        }
    
    # ==================== METADATA ====================
    
    def get_all_metadata(self, force_reload: bool = False) -> Dict:
        """
        Get all stock metadata.
        
        Args:
            force_reload: Force reload from file
            
        Returns:
            Complete metadata dictionary
        """
        return self._load_metadata(force_reload)
    
    def get_stock_metadata(self, symbol: str, force_reload: bool = False) -> Optional[Dict]:
        """
        Get metadata for a single stock.
        
        Args:
            symbol: Stock symbol
            force_reload: Force reload from file
            
        Returns:
            Stock metadata dictionary or None
        """
        metadata = self._load_metadata(force_reload)
        return metadata.get(symbol)
    
    def get_stocks_by_field(self, field: str, value: Any) -> List[str]:
        """
        Find stocks where field matches value.
        
        Args:
            field: Field name (e.g., 'SECTOR', 'BROAD_SECTOR')
            value: Value to match
            
        Returns:
            List of matching symbols
        """
        metadata = self._load_metadata()
        return [symbol for symbol, data in metadata.items() 
                if data.get(field) == value]
    
    def get_stocks_by_index(self, index_name: str) -> List[str]:
        """
        Get all stocks in a specific index.
        
        Args:
            index_name: Index name (e.g., 'NIFTY 50', 'NIFTY SMALLCAP 100')
            
        Returns:
            List of symbols in the index
        """
        metadata = self._load_metadata()
        result = []
        
        for symbol, data in metadata.items():
            indices = data.get('INDICES', '')
            if not indices:
                continue
            
            # Handle both string and list formats
            if isinstance(indices, str):
                if index_name in indices:
                    result.append(symbol)
            elif isinstance(indices, list):
                if index_name in indices:
                    result.append(symbol)
        
        return result
    
    def get_stocks_by_sector(self, sector: str, level: str = 'SECTOR') -> List[str]:
        """
        Get stocks by sector classification.
        
        Args:
            sector: Sector name
            level: Sector level ('BROAD_SECTOR', 'SECTOR_GROUP', 'SECTOR', 'SUB_SECTOR')
            
        Returns:
            List of matching symbols
        """
        return self.get_stocks_by_field(level, sector)
    
    def get_stocks_by_market_cap(self, min_cap: Optional[float] = None,
                                  max_cap: Optional[float] = None) -> List[str]:
        """
        Filter stocks by market cap range.
        
        Args:
            min_cap: Minimum market cap in Cr (None for no limit)
            max_cap: Maximum market cap in Cr (None for no limit)
            
        Returns:
            List of matching symbols
        """
        metadata = self._load_metadata()
        result = []
        
        for symbol, data in metadata.items():
            market_cap = data.get('MARKET_CAP')
            if not market_cap:
                continue
            
            try:
                cap_value = float(str(market_cap).replace(',', ''))
                
                if min_cap is not None and cap_value < min_cap:
                    continue
                if max_cap is not None and cap_value > max_cap:
                    continue
                
                result.append(symbol)
            except:
                continue
        
        return result
    
    # ==================== COMBINED DATA ====================
    
    def get_stock_complete(self, symbol: str, days: int = 252) -> Optional[Dict]:
        """
        Get complete stock information (metadata + recent price data).
        
        Args:
            symbol: Stock symbol
            days: Number of days of price data
            
        Returns:
            Dict with metadata, price_data, and price_stats
        """
        metadata = self.get_stock_metadata(symbol)
        price_df = self.get_price_data(symbol)
        
        if metadata is None:
            return None
        
        result = {
            'symbol': symbol,
            'metadata': metadata,
            'price_data': None,
            'price_stats': None
        }
        
        if price_df is not None and len(price_df) > 0:
            result['price_data'] = price_df.tail(days)
            result['price_stats'] = self.get_price_range(symbol, days)
        
        return result
    
    def get_multiple_stocks(self, symbols: List[str], 
                           include_prices: bool = False,
                           days: int = 30) -> Dict[str, Dict]:
        """
        Get data for multiple stocks efficiently.
        
        Args:
            symbols: List of stock symbols
            include_prices: Whether to include price data
            days: Number of days of price data if include_prices=True
            
        Returns:
            Dict mapping symbol to stock data
        """
        result = {}
        
        for symbol in symbols:
            if include_prices:
                data = self.get_stock_complete(symbol, days)
            else:
                metadata = self.get_stock_metadata(symbol)
                data = {'symbol': symbol, 'metadata': metadata} if metadata else None
            
            if data:
                result[symbol] = data
        
        return result
    
    # ==================== UTILITY METHODS ====================
    
    def get_available_symbols(self) -> List[str]:
        """Get list of all symbols with price data."""
        if not self.raw_dir.exists():
            return []
        
        csv_files = list(self.raw_dir.glob("*.csv"))
        return [f.stem for f in csv_files]
    
    def get_enriched_symbols(self) -> List[str]:
        """Get list of symbols with enriched metadata."""
        metadata = self._load_metadata()
        # Consider enriched if has MARKET_CAP or SHAREHOLDING_PATTERN
        return [symbol for symbol, data in metadata.items()
                if 'MARKET_CAP' in data or 'SHAREHOLDING_PATTERN' in data]
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Get basic info about a symbol.
        
        Returns:
            Dict with has_price_data, has_metadata, has_enrichment
        """
        return {
            'symbol': symbol,
            'has_price_data': (self.raw_dir / f"{symbol}.csv").exists(),
            'has_metadata': symbol in self._load_metadata(),
            'has_enrichment': symbol in self.get_enriched_symbols(),
            'metadata': self.get_stock_metadata(symbol)
        }
    
    def search_stocks(self, query: str, 
                     search_fields: Optional[List[str]] = None) -> List[str]:
        """
        Search for stocks by name or symbol.
        
        Args:
            query: Search query
            search_fields: Fields to search in (default: ['SYMBOL', 'NAME OF COMPANY'])
            
        Returns:
            List of matching symbols
        """
        if search_fields is None:
            search_fields = ['SYMBOL', 'NAME OF COMPANY']
        
        metadata = self._load_metadata()
        query_lower = query.lower()
        matches = []
        
        for symbol, data in metadata.items():
            for field in search_fields:
                value = data.get(field, '')
                if query_lower in str(value).lower():
                    matches.append(symbol)
                    break
        
        return matches
    
    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics about available data.
        
        Returns:
            Dict with counts and statistics
        """
        metadata = self._load_metadata()
        available_symbols = self.get_available_symbols()
        enriched_symbols = self.get_enriched_symbols()
        
        # Get unique indices
        all_indices = set()
        for data in metadata.values():
            indices = data.get('INDICES', '')
            if indices:
                # Handle both string and list formats
                if isinstance(indices, str):
                    all_indices.update([idx.strip() for idx in indices.split(',')])
                elif isinstance(indices, list):
                    all_indices.update([idx.strip() for idx in indices])
        
        return {
            'total_stocks_in_metadata': len(metadata),
            'stocks_with_price_data': len(available_symbols),
            'enriched_stocks': len(enriched_symbols),
            'available_indices': sorted(list(all_indices)),
            'index_count': len(all_indices)
        }


if __name__ == "__main__":
    # Example usage
    reader = DataReader()
    
    print("="*70)
    print("DATA READER - SUMMARY")
    print("="*70)
    
    # Get summary
    stats = reader.get_summary_stats()
    print(f"\nTotal stocks: {stats['total_stocks_in_metadata']}")
    print(f"With price data: {stats['stocks_with_price_data']}")
    print(f"Enriched: {stats['enriched_stocks']}")
    print(f"Available indices: {stats['index_count']}")
    
    # Example stock
    symbol = "HDFCBANK"
    print(f"\n{'='*70}")
    print(f"EXAMPLE: {symbol}")
    print(f"{'='*70}")
    
    info = reader.get_symbol_info(symbol)
    print(f"\nHas price data: {info['has_price_data']}")
    print(f"Has metadata: {info['has_metadata']}")
    print(f"Has enrichment: {info['has_enrichment']}")
    
    if info['has_metadata']:
        metadata = info['metadata']
        print(f"\nName: {metadata.get('NAME OF COMPANY')}")
        print(f"Sector: {metadata.get('SECTOR', 'N/A')}")
        print(f"Market Cap: {metadata.get('MARKET_CAP', 'N/A')} Cr")
    
    if info['has_price_data']:
        price_stats = reader.get_price_range(symbol, days=30)
        if price_stats:
            print(f"\n30-day price range:")
            print(f"  High: ₹{price_stats['high']:.2f}")
            print(f"  Low: ₹{price_stats['low']:.2f}")
            print(f"  Current: ₹{price_stats['current']:.2f}")
            print(f"  Change: {price_stats['change_pct']:+.2f}%")
    
    print(f"\n{'='*70}\n")
