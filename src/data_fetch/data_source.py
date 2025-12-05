"""
Abstract base class for data sources.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime, date
from src.utils.logger import get_logger
from src.utils.exceptions import DataFetchError

logger = get_logger(__name__)


class DataSource(ABC):
    """
    Abstract base class for all data sources.
    
    All data source implementations must inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, name: str):
        """
        Initialize data source.
        
        Args:
            name: Name of the data source
        """
        self.name = name
        self.logger = get_logger(f"{__name__}.{name}")
    
    @abstractmethod
    def fetch_historical(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data.
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
            Returns None if data cannot be fetched
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this data source is available.
        
        Returns:
            True if source is available, False otherwise
        """
        pass
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate fetched data.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            True if data is valid, False otherwise
        """
        if df is None or df.empty:
            return False
        
        # Check for required columns (case-insensitive)
        required_cols = {'date', 'open', 'high', 'low', 'close', 'volume'}
        df_cols = {col.lower() for col in df.columns}
        
        if not required_cols.issubset(df_cols):
            self.logger.warning(f"Missing required columns. Has: {df_cols}, needs: {required_cols}")
            return False
        
        # Check for reasonable data
        if len(df) == 0:
            return False
        
        return True
    
    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to: Date, Open, High, Low, Close, Volume.
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with standardized columns
        """
        if df is None or df.empty:
            return df
        
        # Create column mapping (case-insensitive)
        col_map = {}
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ['date', 'timestamp', 'datetime']:
                col_map[col] = 'Date'
            elif col_lower in ['open', 'o']:
                col_map[col] = 'Open'
            elif col_lower in ['high', 'h']:
                col_map[col] = 'High'
            elif col_lower in ['low', 'l']:
                col_map[col] = 'Low'
            elif col_lower in ['close', 'c', 'price', 'ltp']:
                col_map[col] = 'Close'
            elif col_lower in ['volume', 'vol', 'v']:
                col_map[col] = 'Volume'
        
        df = df.rename(columns=col_map)
        
        # Ensure Date is datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        
        return df
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
