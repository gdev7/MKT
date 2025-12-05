"""
Data normalization utilities for stock market data.
"""
import pandas as pd
import numpy as np
from typing import Optional, Literal
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataNormalizer:
    """Handles data normalization operations for stock data."""
    
    def __init__(self):
        """Initialize the data normalizer."""
        self.logger = get_logger(__name__)
    
    def normalize_prices(
        self,
        df: pd.DataFrame,
        method: Literal['minmax', 'zscore', 'log', 'pct'] = 'minmax',
        columns: Optional[list] = None
    ) -> pd.DataFrame:
        """
        Normalize price data using various methods.
        
        Args:
            df: Input dataframe
            method: Normalization method
                - 'minmax': Scale to [0, 1] range
                - 'zscore': Standardize to mean=0, std=1
                - 'log': Log transformation
                - 'pct': Percentage change from first value
            columns: Columns to normalize (default: OHLC columns)
        
        Returns:
            Dataframe with normalized values
        """
        if columns is None:
            columns = ['OPEN', 'HIGH', 'LOW', 'CLOSE']
        
        df_norm = df.copy()
        
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == 'minmax':
                df_norm[col] = self._minmax_scale(df[col])
            elif method == 'zscore':
                df_norm[col] = self._zscore_normalize(df[col])
            elif method == 'log':
                df_norm[col] = self._log_transform(df[col])
            elif method == 'pct':
                df_norm[col] = self._percentage_change(df[col])
            else:
                raise ValueError(f"Unknown normalization method: {method}")
        
        return df_norm
    
    def _minmax_scale(self, series: pd.Series) -> pd.Series:
        """
        Min-max normalization to [0, 1] range.
        
        Args:
            series: Input series
        
        Returns:
            Normalized series
        """
        min_val = series.min()
        max_val = series.max()
        
        if max_val == min_val:
            return pd.Series(0.5, index=series.index)
        
        return (series - min_val) / (max_val - min_val)
    
    def _zscore_normalize(self, series: pd.Series) -> pd.Series:
        """
        Z-score normalization (standardization).
        
        Args:
            series: Input series
        
        Returns:
            Normalized series
        """
        mean = series.mean()
        std = series.std()
        
        if std == 0:
            return pd.Series(0, index=series.index)
        
        return (series - mean) / std
    
    def _log_transform(self, series: pd.Series) -> pd.Series:
        """
        Log transformation.
        
        Args:
            series: Input series
        
        Returns:
            Log-transformed series
        """
        # Add small constant to avoid log(0)
        return np.log(series + 1e-10)
    
    def _percentage_change(self, series: pd.Series) -> pd.Series:
        """
        Percentage change from first value.
        
        Args:
            series: Input series
        
        Returns:
            Percentage change series
        """
        first_val = series.iloc[0]
        
        if first_val == 0:
            return pd.Series(0, index=series.index)
        
        return (series / first_val - 1) * 100
    
    def normalize_volume(
        self,
        df: pd.DataFrame,
        method: Literal['log', 'zscore', 'minmax'] = 'log'
    ) -> pd.DataFrame:
        """
        Normalize volume data.
        
        Args:
            df: Input dataframe
            method: Normalization method
        
        Returns:
            Dataframe with normalized volume
        """
        if 'VOLUME' not in df.columns:
            return df
        
        df_norm = df.copy()
        
        if method == 'log':
            df_norm['VOLUME'] = np.log(df['VOLUME'] + 1)
        elif method == 'zscore':
            df_norm['VOLUME'] = self._zscore_normalize(df['VOLUME'])
        elif method == 'minmax':
            df_norm['VOLUME'] = self._minmax_scale(df['VOLUME'])
        
        return df_norm
    
    def calculate_returns(
        self,
        df: pd.DataFrame,
        method: Literal['simple', 'log'] = 'simple',
        periods: int = 1
    ) -> pd.DataFrame:
        """
        Calculate price returns.
        
        Args:
            df: Input dataframe
            method: Return calculation method
                - 'simple': (P1 - P0) / P0
                - 'log': ln(P1 / P0)
            periods: Number of periods for return calculation
        
        Returns:
            Dataframe with returns column added
        """
        if 'CLOSE' not in df.columns:
            return df
        
        df_ret = df.copy()
        
        if method == 'simple':
            df_ret['RETURN'] = df['CLOSE'].pct_change(periods=periods)
        elif method == 'log':
            df_ret['RETURN'] = np.log(df['CLOSE'] / df['CLOSE'].shift(periods))
        else:
            raise ValueError(f"Unknown return method: {method}")
        
        return df_ret
    
    def resample_ohlcv(
        self,
        df: pd.DataFrame,
        timeframe: Literal['W', 'M', 'Q', 'Y'] = 'W'
    ) -> pd.DataFrame:
        """
        Resample OHLCV data to different timeframes.
        
        Args:
            df: Input dataframe with DATE index
            timeframe: Target timeframe
                - 'W': Weekly
                - 'M': Monthly
                - 'Q': Quarterly
                - 'Y': Yearly
        
        Returns:
            Resampled dataframe
        """
        if 'DATE' not in df.columns:
            return df
        
        df_resample = df.copy()
        df_resample = df_resample.set_index('DATE')
        
        # Resample OHLCV data
        resampled = pd.DataFrame()
        
        if 'OPEN' in df_resample.columns:
            resampled['OPEN'] = df_resample['OPEN'].resample(timeframe).first()
        
        if 'HIGH' in df_resample.columns:
            resampled['HIGH'] = df_resample['HIGH'].resample(timeframe).max()
        
        if 'LOW' in df_resample.columns:
            resampled['LOW'] = df_resample['LOW'].resample(timeframe).min()
        
        if 'CLOSE' in df_resample.columns:
            resampled['CLOSE'] = df_resample['CLOSE'].resample(timeframe).last()
        
        if 'VOLUME' in df_resample.columns:
            resampled['VOLUME'] = df_resample['VOLUME'].resample(timeframe).sum()
        
        # Reset index
        resampled = resampled.reset_index()
        
        self.logger.info(f"Resampled data from {len(df)} to {len(resampled)} rows ({timeframe})")
        
        return resampled
    
    def adjust_for_splits(
        self,
        df: pd.DataFrame,
        split_ratio: float,
        split_date: str
    ) -> pd.DataFrame:
        """
        Adjust historical prices for stock splits.
        
        Args:
            df: Input dataframe
            split_ratio: Split ratio (e.g., 2.0 for 1:2 split)
            split_date: Date of split (YYYY-MM-DD)
        
        Returns:
            Adjusted dataframe
        """
        df_adj = df.copy()
        
        if 'DATE' not in df.columns:
            return df_adj
        
        # Convert split_date to datetime
        split_dt = pd.to_datetime(split_date)
        
        # Adjust prices before split date
        mask = df_adj['DATE'] < split_dt
        
        price_cols = ['OPEN', 'HIGH', 'LOW', 'CLOSE']
        for col in price_cols:
            if col in df_adj.columns:
                df_adj.loc[mask, col] /= split_ratio
        
        # Adjust volume
        if 'VOLUME' in df_adj.columns:
            df_adj.loc[mask, 'VOLUME'] *= split_ratio
        
        self.logger.info(f"Adjusted prices for {split_ratio}:1 split on {split_date}")
        
        return df_adj
    
    def winsorize(
        self,
        df: pd.DataFrame,
        columns: Optional[list] = None,
        lower_percentile: float = 0.01,
        upper_percentile: float = 0.99
    ) -> pd.DataFrame:
        """
        Winsorize data by clipping extreme values at percentiles.
        
        Args:
            df: Input dataframe
            columns: Columns to winsorize (default: all numeric)
            lower_percentile: Lower percentile threshold (0-1)
            upper_percentile: Upper percentile threshold (0-1)
        
        Returns:
            Winsorized dataframe
        """
        df_wins = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
            # Exclude DATE column if present
            columns = [c for c in columns if c != 'DATE']
        
        for col in columns:
            if col not in df.columns:
                continue
            
            lower_bound = df[col].quantile(lower_percentile)
            upper_bound = df[col].quantile(upper_percentile)
            
            df_wins[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df_wins
