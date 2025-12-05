"""
NSEPython data source implementation.
"""
import pandas as pd
from datetime import date, datetime
from typing import Optional
from src.data_fetch.data_source import DataSource
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NSEPythonSource(DataSource):
    """Data source using nsepython library."""
    
    def __init__(self):
        """Initialize NSEPython data source."""
        super().__init__(name="NSEPython")
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Check if nsepython is available."""
        try:
            import nsepython as nse
            self._nse = nse
            self._available = True
            self.logger.info("nsepython is available")
        except ImportError:
            self._available = False
            self.logger.warning("nsepython is not installed. Install with: pip install nsepython")
    
    def is_available(self) -> bool:
        """Check if nsepython is available."""
        return self._available
    
    def fetch_historical(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data using nsepython.
        
        Args:
            symbol: Stock symbol (without .NS suffix)
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with OHLCV data or None
        """
        if not self.is_available():
            self.logger.error("nsepython is not available")
            return None
        
        try:
            # Convert dates to NSE format (DD-MM-YYYY)
            start_str = start_date.strftime("%d-%m-%Y")
            end_str = end_date.strftime("%d-%m-%Y")
            
            self.logger.debug(f"Fetching {symbol} from NSE: {start_str} to {end_str}")
            
            # Fetch data using nsepython
            data = self._nse.equity_history(
                symbol=symbol,
                series="EQ",  # Equity series
                start_date=start_str,
                end_date=end_str
            )
            
            if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                self.logger.warning(f"No data returned for {symbol}")
                return None
            
            # Convert to DataFrame if needed
            if not isinstance(data, pd.DataFrame):
                data = pd.DataFrame(data)
            
            # NSEPython returns different column names, standardize them
            # Common columns: CH_TIMESTAMP, CH_OPENING_PRICE, CH_TRADE_HIGH_PRICE, 
            # CH_TRADE_LOW_PRICE, CH_CLOSING_PRICE, CH_TOT_TRADED_QTY
            
            column_mapping = {
                'CH_TIMESTAMP': 'Date',
                'CH_OPENING_PRICE': 'Open',
                'CH_TRADE_HIGH_PRICE': 'High',
                'CH_TRADE_LOW_PRICE': 'Low',
                'CH_CLOSING_PRICE': 'Close',
                'CH_TOT_TRADED_QTY': 'Volume',
                'CH_TOT_TRADED_VAL': 'Value',
                # Alternative column names
                'TIMESTAMP': 'Date',
                'OPEN_PRICE': 'Open',
                'HIGH_PRICE': 'High',
                'LOW_PRICE': 'Low',
                'CLOSE_PRICE': 'Close',
                'TTL_TRD_QNTY': 'Volume',
            }
            
            # Rename columns
            for old_col, new_col in column_mapping.items():
                if old_col in data.columns:
                    data = data.rename(columns={old_col: new_col})
            
            # Standardize columns
            data = self.standardize_columns(data)
            
            # Select only required columns
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            available_cols = [col for col in required_cols if col in data.columns]
            data = data[available_cols]
            
            # Ensure Date is datetime
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date'])
            
            # Sort by date
            data = data.sort_values('Date').reset_index(drop=True)
            
            # Validate
            if not self.validate_data(data):
                self.logger.error(f"Data validation failed for {symbol}")
                return None
            
            self.logger.info(f"Fetched {len(data)} records for {symbol} from NSE")
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching {symbol} from NSEPython: {e}")
            return None
    
    def fetch_quote(self, symbol: str) -> Optional[dict]:
        """
        Fetch current quote for a symbol.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with quote data or None
        """
        if not self.is_available():
            return None
        
        try:
            quote = self._nse.nse_quote_ltp(symbol)
            return quote
        except Exception as e:
            self.logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
