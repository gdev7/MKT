"""
Stock Selector - Select stocks for backtesting based on various criteria.

Supports:
- All stocks
- Single stock
- Index constituents (NIFTY 50, NIFTY 100, etc.)
- Sector-based selection
- Custom lists
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict
from src.config import settings
from src.utils.logger import get_logger
from src.utils.data_reader import DataReader

logger = get_logger(__name__)


class StockSelector:
    """Select stocks for backtesting based on various criteria."""
    
    def __init__(self):
        """Initialize stock selector."""
        self.data_reader = DataReader()
        self.metadata = self.data_reader.get_all_metadata()
    
    def get_all_stocks(self) -> List[str]:
        """
        Get all available stocks.
        
        Returns:
            List of all stock symbols
        """
        symbols = list(self.metadata.keys())
        logger.info(f"Selected ALL stocks: {len(symbols)} symbols")
        return symbols
    
    def get_single_stock(self, symbol: str) -> List[str]:
        """
        Get a single stock.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            List with single symbol if valid, empty list otherwise
        """
        symbol = symbol.upper()
        
        if symbol not in self.metadata:
            logger.error(f"Stock {symbol} not found in metadata")
            return []
        
        logger.info(f"Selected single stock: {symbol}")
        return [symbol]
    
    def get_by_index(self, index_name: str) -> List[str]:
        """
        Get stocks that are part of a specific index.
        
        Args:
            index_name: Name of the index (e.g., 'NIFTY 50', 'NIFTY 100')
        
        Returns:
            List of symbols in the index
        """
        index_name = index_name.upper().strip()
        
        # Common index name variations
        index_aliases = {
            'NIFTY50': 'NIFTY 50',
            'NIFTY_50': 'NIFTY 50',
            'NIFTY100': 'NIFTY 100',
            'NIFTY_100': 'NIFTY 100',
            'NIFTY500': 'NIFTY 500',
            'NIFTY_500': 'NIFTY 500',
            'NIFTYMIDCAP100': 'NIFTY MIDCAP 100',
            'NIFTY_MIDCAP_100': 'NIFTY MIDCAP 100',
            'NIFTYSMALLCAP100': 'NIFTY SMALLCAP 100',
            'NIFTY_SMALLCAP_100': 'NIFTY SMALLCAP 100',
        }
        
        # Normalize index name
        if index_name in index_aliases:
            index_name = index_aliases[index_name]
        
        # Use DataReader to get index constituents
        symbols = self.data_reader.get_stocks_by_index(index_name)
        
        if not symbols:
            logger.warning(f"No stocks found for index: {index_name}")
            logger.info("Available indices can be found using list_available_indices()")
        else:
            logger.info(f"Selected {len(symbols)} stocks from {index_name}")
        
        return symbols
    
    def get_by_sector(self, sector: str) -> List[str]:
        """
        Get stocks from a specific sector.
        
        Args:
            sector: Sector name (e.g., 'IT', 'Banking', 'Pharma')
        
        Returns:
            List of symbols in the sector
        """
        sector = sector.upper().strip()
        
        symbols = []
        for symbol, info in self.metadata.items():
            stock_sector = info.get('SECTOR', '').upper()
            if sector in stock_sector or stock_sector in sector:
                symbols.append(symbol)
        
        if not symbols:
            logger.warning(f"No stocks found for sector: {sector}")
        else:
            logger.info(f"Selected {len(symbols)} stocks from sector: {sector}")
        
        return symbols
    
    def get_by_industry(self, industry: str) -> List[str]:
        """
        Get stocks from a specific industry.
        
        Args:
            industry: Industry name
        
        Returns:
            List of symbols in the industry
        """
        industry = industry.upper().strip()
        
        symbols = []
        for symbol, info in self.metadata.items():
            stock_industry = info.get('INDUSTRY', '').upper()
            if industry in stock_industry or stock_industry in industry:
                symbols.append(symbol)
        
        if not symbols:
            logger.warning(f"No stocks found for industry: {industry}")
        else:
            logger.info(f"Selected {len(symbols)} stocks from industry: {industry}")
        
        return symbols
    
    def get_by_custom_list(self, symbols: List[str]) -> List[str]:
        """
        Get stocks from a custom list.
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            List of valid symbols (filters out invalid ones)
        """
        valid_symbols = []
        invalid_symbols = []
        
        for symbol in symbols:
            symbol = symbol.upper().strip()
            if symbol in self.metadata:
                valid_symbols.append(symbol)
            else:
                invalid_symbols.append(symbol)
        
        if invalid_symbols:
            logger.warning(f"Invalid symbols skipped: {', '.join(invalid_symbols)}")
        
        logger.info(f"Selected {len(valid_symbols)} stocks from custom list")
        return valid_symbols
    
    def get_by_criteria(
        self,
        selection_type: str = 'all',
        value: Optional[str] = None,
        custom_list: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get stocks based on flexible criteria.
        
        Args:
            selection_type: Type of selection ('all', 'single', 'index', 'sector', 'industry', 'custom')
            value: Value for the selection (symbol, index name, sector name, etc.)
            custom_list: List of symbols for custom selection
        
        Returns:
            List of selected stock symbols
        """
        selection_type = selection_type.lower()
        
        if selection_type == 'all':
            return self.get_all_stocks()
        
        elif selection_type == 'single':
            if not value:
                logger.error("Symbol required for single stock selection")
                return []
            return self.get_single_stock(value)
        
        elif selection_type == 'index':
            if not value:
                logger.error("Index name required for index selection")
                return []
            return self.get_by_index(value)
        
        elif selection_type == 'sector':
            if not value:
                logger.error("Sector name required for sector selection")
                return []
            return self.get_by_sector(value)
        
        elif selection_type == 'industry':
            if not value:
                logger.error("Industry name required for industry selection")
                return []
            return self.get_by_industry(value)
        
        elif selection_type == 'custom':
            if not custom_list:
                logger.error("Custom list required for custom selection")
                return []
            return self.get_by_custom_list(custom_list)
        
        else:
            logger.error(f"Unknown selection type: {selection_type}")
            return []
    
    def list_available_indices(self) -> Dict[str, int]:
        """
        List all available indices with stock count.
        
        Returns:
            Dictionary of {index_name: stock_count}
        """
        index_counts = {}
        
        for symbol, info in self.metadata.items():
            indices = info.get('INDICES', [])
            if isinstance(indices, list):
                for idx in indices:
                    index_counts[idx] = index_counts.get(idx, 0) + 1
        
        # Sort by stock count
        sorted_indices = dict(sorted(index_counts.items(), key=lambda x: x[1], reverse=True))
        return sorted_indices
    
    def list_available_sectors(self) -> Dict[str, int]:
        """
        List all available sectors with stock count.
        
        Returns:
            Dictionary of {sector_name: stock_count}
        """
        sector_counts = {}
        
        for symbol, info in self.metadata.items():
            sector = info.get('SECTOR', '').strip()
            if sector:
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        sorted_sectors = dict(sorted(sector_counts.items(), key=lambda x: x[1], reverse=True))
        return sorted_sectors
    
    def list_available_industries(self) -> Dict[str, int]:
        """
        List all available industries with stock count.
        
        Returns:
            Dictionary of {industry_name: stock_count}
        """
        industry_counts = {}
        
        for symbol, info in self.metadata.items():
            industry = info.get('INDUSTRY', '').strip()
            if industry:
                industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        sorted_industries = dict(sorted(industry_counts.items(), key=lambda x: x[1], reverse=True))
        return sorted_industries
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        Get detailed information about a stock.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with stock information
        """
        symbol = symbol.upper()
        return self.metadata.get(symbol, {})
    
    def filter_by_data_availability(
        self,
        symbols: List[str],
        min_days: int = 252  # 1 year of data
    ) -> List[str]:
        """
        Filter symbols by data availability.
        
        Args:
            symbols: List of symbols to filter
            min_days: Minimum number of days of data required
        
        Returns:
            List of symbols with sufficient data
        """
        valid_symbols = []
        
        for symbol in symbols:
            csv_path = Path(settings.DATA_RAW_DIR) / f"{symbol}.csv"
            
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path, parse_dates=['Date'])
                    if len(df) >= min_days:
                        valid_symbols.append(symbol)
                    else:
                        logger.debug(f"{symbol}: Only {len(df)} days of data (need {min_days})")
                except Exception as e:
                    logger.debug(f"{symbol}: Error reading data - {e}")
            else:
                logger.debug(f"{symbol}: Data file not found")
        
        logger.info(f"Filtered to {len(valid_symbols)}/{len(symbols)} stocks with sufficient data")
        return valid_symbols


def load_stock_data(symbols: List[str], data_reader: Optional[DataReader] = None) -> Dict[str, pd.DataFrame]:
    """
    Load historical data for multiple stocks.
    
    Args:
        symbols: List of stock symbols
        data_reader: DataReader instance (creates new one if None)
    
    Returns:
        Dictionary of {symbol: DataFrame}
    """
    if data_reader is None:
        data_reader = DataReader()
    
    stock_data = {}
    
    logger.info(f"Loading data for {len(symbols)} stocks...")
    
    for symbol in symbols:
        df = data_reader.get_price_data(symbol)
        
        if df is not None:
            stock_data[symbol] = df
            logger.debug(f"Loaded {symbol}: {len(df)} records")
        else:
            logger.warning(f"Data file not found for {symbol}")
    
    logger.info(f"Successfully loaded {len(stock_data)} stocks")
    return stock_data
