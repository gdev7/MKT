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


class BaseAnalyzer(ABC):
    """Base class for all stock analyzers."""
    
    def __init__(self):
        """Initialize the base analyzer."""
        self.metadata = self._load_metadata()
        self.raw_dir = settings.DATA_RAW_DIR
        
    def _load_metadata(self) -> Dict[str, Any]:
        """Load stocks metadata from JSON file."""
        if not os.path.exists(settings.METADATA_FILE):
            raise FileNotFoundError(f"Metadata file not found: {settings.METADATA_FILE}")
        
        with open(settings.METADATA_FILE, 'r') as f:
            return json.load(f)
    
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
        file_path = os.path.join(self.raw_dir, f"{symbol}.csv")
        
        if not os.path.exists(file_path):
            print(f"Data file not found for {symbol}")
            return None
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Remove the Ticker and Date rows (first two rows after header)
            # These rows have non-numeric data in the Price column
            if len(df) > 2:
                # Check if first row contains 'Ticker'
                if df.iloc[0, 0] == 'Ticker':
                    df = df.iloc[2:]  # Skip first two rows
                    df.reset_index(drop=True, inplace=True)
            
            # Standardize column names
            df.columns = [col.strip().upper() for col in df.columns]
            
            # Rename 'PRICE' column to 'CLOSE' for consistency
            if 'PRICE' in df.columns:
                df.rename(columns={'PRICE': 'DATE'}, inplace=True)
            
            # Parse date column
            if 'DATE' in df.columns:
                df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
                df = df.dropna(subset=['DATE'])  # Drop rows with invalid dates
                df = df.sort_values('DATE')
                df.reset_index(drop=True, inplace=True)
            
            # Convert numeric columns
            numeric_cols = ['CLOSE', 'OPEN', 'HIGH', 'LOW', 'VOLUME']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Drop rows with all NaN values
            df = df.dropna(how='all')
            
            return df
        except Exception as e:
            print(f"Error loading data for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
