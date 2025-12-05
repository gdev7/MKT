"""
Multi-source data fetcher with automatic fallback.
"""
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Optional, List
from src.data_fetch.data_source import DataSource
from src.data_fetch.nsepython_source import NSEPythonSource
from src.data_fetch.yfinance_source import YFinanceSource
from src.data_fetch.nse_official_source import NSEOfficialSource
from src.utils.logger import get_logger
from src.utils.exceptions import DataFetchError

logger = get_logger(__name__)


class MultiSourceFetcher:
    """
    Fetches data from multiple sources with automatic fallback.
    
    Priority order:
    1. NSEPython (free, direct NSE data)
    2. NSE Official API (direct but has limitations)
    3. YFinance (reliable fallback)
    
    The fetcher will try each source in order until data is successfully retrieved.
    """
    
    def __init__(self, sources: Optional[List[DataSource]] = None):
        """
        Initialize multi-source fetcher.
        
        Args:
            sources: List of data sources in priority order.
                    If None, uses default sources.
        """
        if sources is None:
            # Default priority order
            self.sources = [
                NSEPythonSource(),
                NSEOfficialSource(),
                YFinanceSource(),
            ]
        else:
            self.sources = sources
        
        # Log available sources
        available = [s.name for s in self.sources if s.is_available()]
        unavailable = [s.name for s in self.sources if not s.is_available()]
        
        logger.info(f"Available sources: {available}")
        if unavailable:
            logger.warning(f"Unavailable sources: {unavailable}")
    
    def fetch(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        preferred_source: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data with automatic fallback.
        
        Args:
            symbol: Stock symbol (without .NS suffix)
            start_date: Start date
            end_date: End date
            preferred_source: Name of preferred source to try first
        
        Returns:
            DataFrame with OHLCV data or None
        """
        # Reorder sources if preferred source specified
        sources = self._get_ordered_sources(preferred_source)
        
        last_error = None
        
        for source in sources:
            if not source.is_available():
                logger.debug(f"Skipping {source.name} (not available)")
                continue
            
            try:
                logger.debug(f"Trying {source.name} for {symbol}")
                
                data = source.fetch_historical(symbol, start_date, end_date)
                
                if data is not None and not data.empty:
                    # Add metadata column
                    data['Source'] = source.name
                    
                    logger.info(f"Successfully fetched {symbol} from {source.name} ({len(data)} records)")
                    return data
                else:
                    logger.debug(f"{source.name} returned no data for {symbol}")
                    
            except Exception as e:
                logger.warning(f"{source.name} failed for {symbol}: {e}")
                last_error = e
                continue
        
        # All sources failed
        logger.error(f"All sources failed for {symbol}")
        if last_error:
            raise DataFetchError(f"Failed to fetch {symbol} from all sources") from last_error
        
        return None
    
    def _get_ordered_sources(self, preferred_source: Optional[str]) -> List[DataSource]:
        """
        Get sources in order, with preferred source first.
        
        Args:
            preferred_source: Name of preferred source
        
        Returns:
            List of sources in priority order
        """
        if preferred_source is None:
            return self.sources
        
        # Find preferred source
        preferred = None
        others = []
        
        for source in self.sources:
            if source.name.lower() == preferred_source.lower():
                preferred = source
            else:
                others.append(source)
        
        # Put preferred first, then others
        if preferred:
            return [preferred] + others
        else:
            logger.warning(f"Preferred source '{preferred_source}' not found, using default order")
            return self.sources
    
    def get_available_sources(self) -> List[str]:
        """
        Get list of available source names.
        
        Returns:
            List of source names that are available
        """
        return [s.name for s in self.sources if s.is_available()]
    
    def get_source_by_name(self, name: str) -> Optional[DataSource]:
        """
        Get source by name.
        
        Args:
            name: Source name
        
        Returns:
            DataSource or None if not found
        """
        for source in self.sources:
            if source.name.lower() == name.lower():
                return source
        return None
