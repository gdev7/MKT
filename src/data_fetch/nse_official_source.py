"""
NSE Official API data source implementation.
"""
import pandas as pd
import requests
from datetime import date, datetime
from typing import Optional
from src.data_fetch.data_source import DataSource
from src.utils.logger import get_logger
from src.config import settings
import time

logger = get_logger(__name__)


class NSEOfficialSource(DataSource):
    """Data source using NSE Official API."""
    
    def __init__(self):
        """Initialize NSE Official data source."""
        super().__init__(name="NSE Official")
        self.session = requests.Session()
        self.base_url = "https://www.nseindia.com"
        self.headers = settings.NSE_HEADERS.copy()
        self._initialize_session()
    
    def _initialize_session(self) -> None:
        """Initialize session with NSE."""
        try:
            # Get cookies by visiting homepage
            response = self.session.get(self.base_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                self._available = True
                self.logger.info("NSE Official API session initialized")
            else:
                self._available = False
                self.logger.warning(f"NSE API returned status {response.status_code}")
        except Exception as e:
            self._available = False
            self.logger.warning(f"Could not initialize NSE session: {e}")
    
    def is_available(self) -> bool:
        """Check if NSE Official API is available."""
        return self._available
    
    def fetch_historical(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data using NSE Official API.
        
        Note: NSE API typically provides data for last 1-2 years only.
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with OHLCV data or None
        """
        if not self.is_available():
            self.logger.error("NSE Official API is not available")
            return None
        
        try:
            # NSE API date format: DD-MM-YYYY
            from_date = start_date.strftime("%d-%m-%Y")
            to_date = end_date.strftime("%d-%m-%Y")
            
            # NSE historical data endpoint
            url = f"{self.base_url}/api/historical/cm/equity"
            
            params = {
                'symbol': symbol,
                'series': '["EQ"]',
                'from': from_date,
                'to': to_date
            }
            
            self.logger.debug(f"Fetching {symbol} from NSE API: {from_date} to {to_date}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
            # Make request
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=settings.API_REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                self.logger.warning(f"NSE API returned status {response.status_code}")
                return None
            
            # Parse JSON response
            json_data = response.json()
            
            if 'data' not in json_data or not json_data['data']:
                self.logger.warning(f"No data in NSE response for {symbol}")
                return None
            
            # Convert to DataFrame
            data = pd.DataFrame(json_data['data'])
            
            # NSE column mapping
            column_mapping = {
                'CH_TIMESTAMP': 'Date',
                'CH_OPENING_PRICE': 'Open',
                'CH_TRADE_HIGH_PRICE': 'High',
                'CH_TRADE_LOW_PRICE': 'Low',
                'CH_CLOSING_PRICE': 'Close',
                'CH_TOT_TRADED_QTY': 'Volume',
                'mTIMESTAMP': 'Date',
                'CH_LAST_TRADED_PRICE': 'Close',
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
            
            # Sort by date
            data = data.sort_values('Date').reset_index(drop=True)
            
            # Validate
            if not self.validate_data(data):
                self.logger.error(f"Data validation failed for {symbol}")
                return None
            
            self.logger.info(f"Fetched {len(data)} records for {symbol} from NSE Official")
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error fetching {symbol} from NSE: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching {symbol} from NSE Official: {e}")
            return None
