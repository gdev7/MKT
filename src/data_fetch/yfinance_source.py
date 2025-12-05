"""
YFinance data source implementation.
"""
import pandas as pd
from datetime import date, timedelta
from typing import Optional
from src.data_fetch.data_source import DataSource
from src.utils.logger import get_logger

logger = get_logger(__name__)


class YFinanceSource(DataSource):
    """Data source using yfinance library."""
    
    def __init__(self):
        """Initialize yfinance data source."""
        super().__init__(name="YFinance")
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Check if yfinance is available."""
        try:
            import yfinance
            self._yf = yfinance
            self._available = True
            self.logger.info("yfinance is available")
        except ImportError:
            self._available = False
            self.logger.warning("yfinance is not installed")
    
    def is_available(self) -> bool:
        """Check if yfinance is available."""
        return self._available
    
    def fetch_historical(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data using yfinance.
        
        Args:
            symbol: Stock symbol (without .NS suffix)
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with OHLCV data or None
        """
        if not self.is_available():
            self.logger.error("yfinance is not available")
            return None
        
        try:
            # Add .NS suffix for NSE stocks
            ticker = f"{symbol}.NS"
            
            self.logger.debug(f"Fetching {ticker} from {start_date} to {end_date}")
            
            # Download data
            data = self._yf.download(
                ticker,
                start=start_date,
                end=end_date + timedelta(days=1),  # Include end_date
                progress=False,
                auto_adjust=False  # Get raw prices
            )
            
            if data.empty:
                self.logger.warning(f"No data returned for {symbol}")
                return None
            
            # Reset index to get Date as column
            data = data.reset_index()
            
            # Handle multi-level columns
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Standardize columns
            data = self.standardize_columns(data)
            
            # Validate
            if not self.validate_data(data):
                self.logger.error(f"Data validation failed for {symbol}")
                return None
            
            self.logger.info(f"Fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching {symbol} from yfinance: {e}")
            return None
