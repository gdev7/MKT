import yfinance as yf
import pandas as pd
import os
import json
import time
from datetime import datetime, timedelta
from tqdm import tqdm
from src.config import settings
from src.data_fetch.multi_source_fetcher import MultiSourceFetcher
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataFetcher:

    def __init__(self, delay=1.0, use_multi_source=True):
        """
        Initialize DataFetcher.
        
        Args:
            delay: Delay between API calls (seconds)
            use_multi_source: If True, use multi-source fetcher with fallback.
                            If False, use yfinance only (legacy mode)
        """
        self.folder = settings.DATA_RAW_DIR
        self.metadata_file = settings.METADATA_FILE
        self.delay = delay
        self.use_multi_source = use_multi_source
        
        # Initialize multi-source fetcher
        if use_multi_source:
            self.multi_fetcher = MultiSourceFetcher()
            logger.info(f"Multi-source mode enabled. Available: {self.multi_fetcher.get_available_sources()}")
        else:
            self.multi_fetcher = None
            logger.info("Legacy mode (yfinance only)")
        
        # Load metadata
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
            self.equity_df = pd.DataFrame.from_dict(self.metadata, orient='index')
        else:
            logger.warning(f"Metadata file not found at {self.metadata_file}")
            self.metadata = {}
            self.equity_df = pd.DataFrame()

    # -------------------------------------------------------
    # Utility: Load CSV if exists
    # -------------------------------------------------------
    def _get_file_path(self, symbol):
        return os.path.join(self.folder, f"{symbol}.csv")

    # -------------------------------------------------------
    # 1. Fetch only new data (incremental update)
    # -------------------------------------------------------
    def fetch_latest(self, symbol):
        """
        Fetch incremental data for a symbol (updates existing CSV).
        
        Args:
            symbol: Stock symbol (without .NS)
        
        Returns:
            DataFrame with updated data
        """
        file_path = self._get_file_path(symbol)

        if os.path.exists(file_path):
            # Check for multi-header format (yfinance artifact)
            try:
                with open(file_path, 'r') as f:
                    first_line = f.readline()
                
                if first_line.startswith("Price"):
                    # Bad format: 3 header lines
                    old_df = pd.read_csv(file_path, header=2, parse_dates=["Date"])
                else:
                    # Standard format
                    old_df = pd.read_csv(file_path, parse_dates=["Date"])
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                return None

            if not old_df.empty:
                last_date = old_df["Date"].max().date()
                start_date = last_date + timedelta(days=1)
            else:
                start_date = datetime(2000, 1, 1).date()
        else:
            logger.warning(f"No old data found for {symbol}. Use fetch_all().")
            return None

        today = datetime.now().date()
        if start_date > today:
            logger.info(f"{symbol} already up-to-date.")
            return None

        logger.info(f"Fetching data for {symbol} from {start_date} to {today}")
        
        # Rate limiting
        time.sleep(self.delay)
        
        try:
            if self.use_multi_source and self.multi_fetcher:
                # Use multi-source fetcher
                new_data = self.multi_fetcher.fetch(symbol, start_date, today)
            else:
                # Legacy yfinance mode
                new_data = yf.download(
                    f"{symbol}.NS",
                    start=start_date,
                    end=today + timedelta(days=1),
                    progress=False,
                )
                
                if not new_data.empty:
                    new_data.reset_index(inplace=True)
                    if isinstance(new_data.columns, pd.MultiIndex):
                        new_data.columns = new_data.columns.get_level_values(0)
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None

        if new_data is None or new_data.empty:
            logger.info(f"No new data for {symbol}.")
            return None

        if os.path.exists(file_path):
             old_df = pd.read_csv(file_path, parse_dates=["Date"])
             final_df = pd.concat([old_df, new_data]).drop_duplicates("Date").sort_values("Date")
        else:
             final_df = new_data

        final_df.to_csv(file_path, index=False)

        logger.info(f"{symbol} updated to {final_df['Date'].max().date()}")
        return final_df

    # -------------------------------------------------------
    # 2. Fetch complete history (default last 20 years)
    # -------------------------------------------------------
    def fetch_all(self, symbol, years=20):
        """
        Fetch complete history for a symbol.
        
        Args:
            symbol: Stock symbol (without .NS)
            years: Number of years of history
        
        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Fetching {years} years data for {symbol}...")

        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=years*365)

        # Rate limiting
        time.sleep(self.delay)

        try:
            if self.use_multi_source and self.multi_fetcher:
                # Use multi-source fetcher
                data = self.multi_fetcher.fetch(symbol, start_date, end_date)
            else:
                # Legacy yfinance mode
                data = yf.download(f"{symbol}.NS", period=f"{years}y", progress=False)
                
                if not data.empty:
                    data.reset_index(inplace=True)
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None

        if data is None or data.empty:
            logger.warning(f"No data found for {symbol}.")
            return None

        # Save to CSV
        data.to_csv(self._get_file_path(symbol), index=False)
        logger.info(f"{symbol} full history saved ({len(data)} records).")
        return data

    # -------------------------------------------------------
    # 3. Fetch only today's data
    # -------------------------------------------------------
    def fetch_today(self, symbol):
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        # Rate limiting
        time.sleep(self.delay)

        try:
            data = yf.download(
                f"{symbol}.NS",
                start=today,
                end=tomorrow,
                progress=False
            )
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

        if data.empty:
            print(f"No data for {symbol} today.")
            return None

        data.reset_index(inplace=True)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        print(f"Today's data for {symbol} fetched.")
        return data

    # -------------------------------------------------------
    # 4. Fetch data using stock tag (example: largecap)
    # -------------------------------------------------------
    def fetch_by_tag(self, tag, latest=False):
        if "TAG" not in self.equity_df.columns:
            print("TAG column not found in metadata.")
            return

        tagged_symbols = self.equity_df[self.equity_df["TAG"] == tag].SYMBOL.tolist()

        print(f"Found {len(tagged_symbols)} stocks with tag '{tag}'.")

        for symbol in tqdm(tagged_symbols, desc=f"Fetching {tag} stocks"):
            if latest:
                self.fetch_latest(symbol)
            else:
                self.fetch_all(symbol)
