"""
Base analyzer class providing common functionality for all stock analyzers.
"""
import os
import json
import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.config import settings
from src.utils.data_reader import DataReader


class BaseAnalyzer(ABC):
    """Base class for all stock analyzers."""
    
    def __init__(self):
        """Initialize the base analyzer."""
        self.data_reader = DataReader()
        self.metadata = self.data_reader.get_all_metadata()
        self.raw_dir = settings.DATA_RAW_DIR
    
    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata information for a stock symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary containing stock metadata or None if not found
        """
        return self.metadata.get(symbol)
    
    def load_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Load historical data for a stock from CSV file.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            DataFrame with stock data or None if file doesn't exist
        """
        df = self.data_reader.get_price_data(symbol)
        
        if df is None:
            print(f"Data file not found for {symbol}")
            return None
        
        # Standardize column names to uppercase for compatibility
        df.columns = [col.strip().upper() for col in df.columns]
        
        return df
    
    def filter_by_date_range(
        self, 
        df: pd.DataFrame, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filter DataFrame by date range.
        
        Args:
            df: DataFrame with DATE column
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Filtered DataFrame
        """
        if 'DATE' not in df.columns:
            return df
        
        filtered_df = df.copy()
        
        if start_date:
            start = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['DATE'] >= start]
        
        if end_date:
            end = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df['DATE'] <= end]
        
        return filtered_df
    
    def get_stocks_by_index(self, index_name: str) -> List[str]:
        """
        Get list of stock symbols that belong to a specific index.
        
        Args:
            index_name: Name of the index (e.g., "NIFTY 50")
            
        Returns:
            List of stock symbols in the index
        """
        stocks = []
        for symbol, info in self.metadata.items():
            if 'INDICES' in info and index_name in info['INDICES']:
                stocks.append(symbol)
        return stocks
    
    def get_all_indices(self) -> List[str]:
        """
        Get list of all unique indices in the metadata.
        
        Returns:
            List of index names
        """
        indices = set()
        for info in self.metadata.values():
            if 'INDICES' in info:
                indices.update(info['INDICES'])
        return sorted(list(indices))
    
    def get_all_symbols(self) -> List[str]:
        """
        Get list of all stock symbols in metadata.
        
        Returns:
            List of stock symbols
        """
        return list(self.metadata.keys())
    
    @abstractmethod
    def analyze(self, *args, **kwargs):
        """
        Abstract method to be implemented by derived classes.
        Each analyzer should implement its own analysis logic.
        """
        pass
