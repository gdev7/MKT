"""
Data cleaning utilities for stock market data.
"""
import pandas as pd
import numpy as np
from typing import Optional, Tuple, List
from src.utils.logger import get_logger
from src.utils.exceptions import ValidationError
from src.utils.constants import REQUIRED_COLUMNS

logger = get_logger(__name__)


class DataCleaner:
    """Handles data cleaning operations for stock data."""
    
    def __init__(self):
        """Initialize the data cleaner."""
        self.logger = get_logger(__name__)
    
    def clean_stock_data(
        self,
        df: pd.DataFrame,
        remove_outliers: bool = True,
        handle_missing: bool = True,
        validate_schema: bool = True
    ) -> pd.DataFrame:
        """
        Perform comprehensive data cleaning on stock data.
        
        Args:
            df: Input dataframe
            remove_outliers: Whether to remove outliers
            handle_missing: Whether to handle missing values
            validate_schema: Whether to validate required columns
        
        Returns:
            Cleaned dataframe
        
        Raises:
            ValidationError: If required columns are missing
        """
        df_clean = df.copy()
        
        # Validate schema
        if validate_schema:
            self._validate_schema(df_clean)
        
        # Remove duplicates
        df_clean = self._remove_duplicates(df_clean)
        
        # Handle missing values
        if handle_missing:
            df_clean = self._handle_missing_values(df_clean)
        
        # Remove outliers
        if remove_outliers:
            df_clean = self._remove_outliers(df_clean)
        
        # Validate OHLC relationship
        df_clean = self._validate_ohlc(df_clean)
        
        # Sort by date
        if 'DATE' in df_clean.columns:
            df_clean = df_clean.sort_values('DATE').reset_index(drop=True)
        
        self.logger.info(f"Cleaned data: {len(df)} -> {len(df_clean)} rows")
        
        return df_clean
    
    def _validate_schema(self, df: pd.DataFrame) -> None:
        """
        Validate that dataframe has required columns.
        
        Args:
            df: Dataframe to validate
        
        Raises:
            ValidationError: If required columns are missing
        """
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_cols:
            raise ValidationError(f"Missing required columns: {missing_cols}")
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate rows based on DATE.
        
        Args:
            df: Input dataframe
        
        Returns:
            Dataframe without duplicates
        """
        if 'DATE' in df.columns:
            before = len(df)
            df = df.drop_duplicates(subset=['DATE'], keep='last')
            after = len(df)
            
            if before > after:
                self.logger.warning(f"Removed {before - after} duplicate dates")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataframe.
        
        Strategy:
        - Drop rows with missing OHLC values
        - Fill missing volume with 0
        
        Args:
            df: Input dataframe
        
        Returns:
            Dataframe with handled missing values
        """
        before = len(df)
        
        # Drop rows with missing OHLC
        ohlc_cols = ['OPEN', 'HIGH', 'LOW', 'CLOSE']
        df = df.dropna(subset=ohlc_cols)
        
        # Fill missing volume with 0
        if 'VOLUME' in df.columns:
            df['VOLUME'] = df['VOLUME'].fillna(0)
        
        after = len(df)
        
        if before > after:
            self.logger.warning(f"Dropped {before - after} rows with missing OHLC values")
        
        return df
    
    def _remove_outliers(
        self,
        df: pd.DataFrame,
        std_threshold: float = 5.0
    ) -> pd.DataFrame:
        """
        Remove outliers based on price changes.
        
        Uses z-score method: removes data points more than std_threshold
        standard deviations away from the mean.
        
        Args:
            df: Input dataframe
            std_threshold: Z-score threshold for outlier detection
        
        Returns:
            Dataframe without outliers
        """
        if len(df) < 30:  # Skip for small datasets
            return df
        
        before = len(df)
        
        # Calculate daily returns
        if 'CLOSE' in df.columns:
            df = df.copy()
            df['RETURN'] = df['CLOSE'].pct_change()
            
            # Calculate z-scores
            mean_return = df['RETURN'].mean()
            std_return = df['RETURN'].std()
            
            if std_return > 0:
                df['Z_SCORE'] = np.abs((df['RETURN'] - mean_return) / std_return)
                
                # Remove outliers
                df = df[df['Z_SCORE'] < std_threshold]
                
                # Drop temporary columns
                df = df.drop(['RETURN', 'Z_SCORE'], axis=1)
        
        after = len(df)
        
        if before > after:
            self.logger.info(f"Removed {before - after} outliers")
        
        return df
    
    def _validate_ohlc(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and fix OHLC relationships.
        
        Ensures: LOW <= OPEN, CLOSE <= HIGH
        
        Args:
            df: Input dataframe
        
        Returns:
            Dataframe with corrected OHLC values
        """
        if not all(col in df.columns for col in ['OPEN', 'HIGH', 'LOW', 'CLOSE']):
            return df
        
        df = df.copy()
        
        # Check for invalid OHLC relationships
        invalid_low = df['LOW'] > df[['OPEN', 'CLOSE', 'HIGH']].min(axis=1)
        invalid_high = df['HIGH'] < df[['OPEN', 'CLOSE', 'LOW']].max(axis=1)
        
        invalid_count = invalid_low.sum() + invalid_high.sum()
        
        if invalid_count > 0:
            self.logger.warning(f"Found {invalid_count} rows with invalid OHLC relationships")
            
            # Fix LOW
            df.loc[invalid_low, 'LOW'] = df.loc[invalid_low, ['OPEN', 'CLOSE', 'HIGH']].min(axis=1)
            
            # Fix HIGH
            df.loc[invalid_high, 'HIGH'] = df.loc[invalid_high, ['OPEN', 'CLOSE', 'LOW']].max(axis=1)
        
        return df
    
    def handle_corporate_actions(
        self,
        df: pd.DataFrame,
        splits: Optional[List[Tuple[str, float]]] = None,
        bonuses: Optional[List[Tuple[str, float]]] = None
    ) -> pd.DataFrame:
        """
        Adjust prices for corporate actions (stock splits, bonuses).
        
        Args:
            df: Input dataframe
            splits: List of (date, ratio) tuples for stock splits
            bonuses: List of (date, ratio) tuples for bonus issues
        
        Returns:
            Adjusted dataframe
        """
        if not splits and not bonuses:
            return df
        
        df = df.copy()
        
        # Handle stock splits
        if splits:
            for split_date, ratio in splits:
                mask = df['DATE'] < pd.to_datetime(split_date)
                
                # Adjust prices
                df.loc[mask, 'OPEN'] /= ratio
                df.loc[mask, 'HIGH'] /= ratio
                df.loc[mask, 'LOW'] /= ratio
                df.loc[mask, 'CLOSE'] /= ratio
                
                # Adjust volume
                df.loc[mask, 'VOLUME'] *= ratio
                
                self.logger.info(f"Applied {ratio}:1 split adjustment for {split_date}")
        
        # Handle bonus issues (similar to splits)
        if bonuses:
            for bonus_date, ratio in bonuses:
                mask = df['DATE'] < pd.to_datetime(bonus_date)
                
                # Adjust prices
                df.loc[mask, 'OPEN'] /= (1 + ratio)
                df.loc[mask, 'HIGH'] /= (1 + ratio)
                df.loc[mask, 'LOW'] /= (1 + ratio)
                df.loc[mask, 'CLOSE'] /= (1 + ratio)
                
                # Adjust volume
                df.loc[mask, 'VOLUME'] *= (1 + ratio)
                
                self.logger.info(f"Applied {ratio} bonus adjustment for {bonus_date}")
        
        return df
    
    def remove_low_volume_days(
        self,
        df: pd.DataFrame,
        min_volume: int = 0,
        percentile: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Remove days with abnormally low volume.
        
        Args:
            df: Input dataframe
            min_volume: Minimum volume threshold (absolute)
            percentile: Percentile threshold (0-100), overrides min_volume
        
        Returns:
            Filtered dataframe
        """
        if 'VOLUME' not in df.columns:
            return df
        
        df = df.copy()
        before = len(df)
        
        if percentile is not None:
            threshold = df['VOLUME'].quantile(percentile / 100)
        else:
            threshold = min_volume
        
        df = df[df['VOLUME'] >= threshold]
        
        after = len(df)
        
        if before > after:
            self.logger.info(f"Removed {before - after} low-volume days (threshold: {threshold})")
        
        return df
