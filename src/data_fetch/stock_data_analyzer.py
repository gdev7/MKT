"""
Stock Data Analyzer Module

This module provides comprehensive analysis and calculation functionality for stock data.
Supports various statistical operations and technical indicators.
"""

import pandas as pd
import numpy as np
from typing import Optional, Union, List
import warnings

warnings.filterwarnings('ignore')


class StockDataAnalyzer:
    """
    A comprehensive analyzer for stock data with various calculation capabilities.
    
    Features:
    - Basic statistics (average, max, min, median, std)
    - Moving averages (SMA, EMA, WMA)
    - Returns calculations
    - Volatility measures
    - Technical indicators
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the StockDataAnalyzer.
        
        Args:
            data: DataFrame with stock data (must have Date column)
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        
        if 'Date' not in data.columns:
            raise ValueError("Data must have a 'Date' column")
        
        self.data = data.copy()
        
        # Ensure Date is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.data['Date']):
            self.data['Date'] = pd.to_datetime(self.data['Date'])
        
        self.data = self.data.sort_values('Date').reset_index(drop=True)
    
    # ==================== Basic Statistics ====================
    
    def average(self, column: str = 'Close') -> float:
        """
        Calculate the average (mean) of a column.
        
        Args:
            column: Column name to calculate average for
        
        Returns:
            Average value
        
        Example:
            >>> analyzer = StockDataAnalyzer(data)
            >>> avg_close = analyzer.average('Close')
            >>> avg_volume = analyzer.average('Volume')
        """
        self._validate_column(column)
        return self.data[column].mean()
    
    def max_value(self, column: str = 'Close') -> dict:
        """
        Get the maximum value and its date.
        
        Args:
            column: Column name to find maximum for
        
        Returns:
            Dictionary with max value, date, and index
        
        Example:
            >>> analyzer = StockDataAnalyzer(data)
            >>> max_close = analyzer.max_value('Close')
            >>> # Returns: {'value': 1500.5, 'date': '2024-01-15', 'index': 42}
        """
        self._validate_column(column)
        idx = self.data[column].idxmax()
        
        return {
            'value': self.data.loc[idx, column],
            'date': self.data.loc[idx, 'Date'].strftime('%Y-%m-%d'),
            'index': idx
        }
    
    def min_value(self, column: str = 'Close') -> dict:
        """
        Get the minimum value and its date.
        
        Args:
            column: Column name to find minimum for
        
        Returns:
            Dictionary with min value, date, and index
        
        Example:
            >>> analyzer = StockDataAnalyzer(data)
            >>> min_close = analyzer.min_value('Close')
            >>> # Returns: {'value': 1200.5, 'date': '2024-03-15', 'index': 15}
        """
        self._validate_column(column)
        idx = self.data[column].idxmin()
        
        return {
            'value': self.data.loc[idx, column],
            'date': self.data.loc[idx, 'Date'].strftime('%Y-%m-%d'),
            'index': idx
        }
    
    def median(self, column: str = 'Close') -> float:
        """
        Calculate the median of a column.
        
        Args:
            column: Column name to calculate median for
        
        Returns:
            Median value
        """
        self._validate_column(column)
        return self.data[column].median()
    
    def std_dev(self, column: str = 'Close') -> float:
        """
        Calculate the standard deviation of a column.
        
        Args:
            column: Column name to calculate std dev for
        
        Returns:
            Standard deviation
        """
        self._validate_column(column)
        return self.data[column].std()
    
    def variance(self, column: str = 'Close') -> float:
        """
        Calculate the variance of a column.
        
        Args:
            column: Column name to calculate variance for
        
        Returns:
            Variance
        """
        self._validate_column(column)
        return self.data[column].var()
    
    def percentile(self, column: str = 'Close', q: float = 0.5) -> float:
        """
        Calculate a specific percentile.
        
        Args:
            column: Column name
            q: Percentile to compute (0.0 to 1.0)
        
        Returns:
            Percentile value
        
        Example:
            >>> analyzer = StockDataAnalyzer(data)
            >>> p25 = analyzer.percentile('Close', 0.25)  # 25th percentile
            >>> p75 = analyzer.percentile('Close', 0.75)  # 75th percentile
        """
        self._validate_column(column)
        return self.data[column].quantile(q)
    
    def summary_stats(self, column: str = 'Close') -> dict:
        """
        Get comprehensive summary statistics for a column.
        
        Args:
            column: Column name
        
        Returns:
            Dictionary with various statistics
        
        Example:
            >>> analyzer = StockDataAnalyzer(data)
            >>> stats = analyzer.summary_stats('Close')
        """
        self._validate_column(column)
        
        return {
            'count': int(self.data[column].count()),
            'mean': float(self.data[column].mean()),
            'median': float(self.data[column].median()),
            'std': float(self.data[column].std()),
            'min': float(self.data[column].min()),
            'max': float(self.data[column].max()),
            'q25': float(self.data[column].quantile(0.25)),
            'q75': float(self.data[column].quantile(0.75)),
            'range': float(self.data[column].max() - self.data[column].min())
        }
    
    # ==================== Moving Averages ====================
    
    def simple_moving_average(self, 
                             column: str = 'Close',
                             window: int = 20,
                             add_to_data: bool = False) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA).
        
        Args:
            column: Column name to calculate SMA for
            window: Window size (number of periods)
            add_to_data: If True, adds SMA column to self.data
        
        Returns:
            Series with SMA values
        
        Example:
            >>> analyzer = StockDataAnalyzer(data)
            >>> sma_20 = analyzer.simple_moving_average('Close', window=20)
            >>> sma_50 = analyzer.simple_moving_average('Close', window=50)
        """
        self._validate_column(column)
        
        sma = self.data[column].rolling(window=window, min_periods=1).mean()
        
        if add_to_data:
            self.data[f'SMA_{window}'] = sma
        
        return sma
    
    def exponential_moving_average(self,
                                   column: str = 'Close',
                                   span: int = 20,
                                   add_to_data: bool = False) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA).
        
        Args:
            column: Column name to calculate EMA for
            span: Span for EMA calculation
            add_to_data: If True, adds EMA column to self.data
        
        Returns:
            Series with EMA values
        
        Example:
            >>> analyzer = StockDataAnalyzer(data)
            >>> ema_12 = analyzer.exponential_moving_average('Close', span=12)
            >>> ema_26 = analyzer.exponential_moving_average('Close', span=26)
        """
        self._validate_column(column)
        
        ema = self.data[column].ewm(span=span, adjust=False).mean()
        
        if add_to_data:
            self.data[f'EMA_{span}'] = ema
        
        return ema
    
    def weighted_moving_average(self,
                                column: str = 'Close',
                                window: int = 20,
                                add_to_data: bool = False) -> pd.Series:
        """
        Calculate Weighted Moving Average (WMA).
        
        Args:
            column: Column name to calculate WMA for
            window: Window size
            add_to_data: If True, adds WMA column to self.data
        
        Returns:
            Series with WMA values
        """
        self._validate_column(column)
        
        weights = np.arange(1, window + 1)
        
        def wma(x):
            if len(x) < window:
                return np.nan
            return np.dot(x[-window:], weights) / weights.sum()
        
        wma_values = self.data[column].rolling(window=window).apply(wma, raw=True)
        
        if add_to_data:
            self.data[f'WMA_{window}'] = wma_values
        
        return wma_values
    
    def cumulative_moving_average(self,
                                  column: str = 'Close',
                                  add_to_data: bool = False) -> pd.Series:
        """
        Calculate Cumulative Moving Average (CMA).
        
        Args:
            column: Column name
            add_to_data: If True, adds CMA column to self.data
        
        Returns:
            Series with CMA values
        """
        self._validate_column(column)
        
        cma = self.data[column].expanding().mean()
        
        if add_to_data:
            self.data['CMA'] = cma
        
        return cma
    
    # ==================== Returns and Changes ====================
    
    def returns(self,
                column: str = 'Close',
                periods: int = 1,
                percentage: bool = True,
                add_to_data: bool = False) -> pd.Series:
        """
        Calculate returns (percentage or absolute change).
        
        Args:
            column: Column name
            periods: Number of periods for return calculation
            percentage: If True, returns percentage change; else absolute change
            add_to_data: If True, adds returns column to self.data
        
        Returns:
            Series with returns
        
        Example:
            >>> analyzer = StockDataAnalyzer(data)
            >>> daily_returns = analyzer.returns('Close', periods=1)
            >>> weekly_returns = analyzer.returns('Close', periods=5)
        """
        self._validate_column(column)
        
        if percentage:
            ret = self.data[column].pct_change(periods=periods) * 100
        else:
            ret = self.data[column].diff(periods=periods)
        
        if add_to_data:
            suffix = f'_pct_change_{periods}' if percentage else f'_diff_{periods}'
            self.data[f'{column}{suffix}'] = ret
        
        return ret
    
    def log_returns(self,
                    column: str = 'Close',
                    periods: int = 1,
                    add_to_data: bool = False) -> pd.Series:
        """
        Calculate logarithmic returns.
        
        Args:
            column: Column name
            periods: Number of periods
            add_to_data: If True, adds log returns column to self.data
        
        Returns:
            Series with log returns
        """
        self._validate_column(column)
        
        log_ret = np.log(self.data[column] / self.data[column].shift(periods))
        
        if add_to_data:
            self.data[f'{column}_log_return_{periods}'] = log_ret
        
        return log_ret
    
    def cumulative_returns(self,
                          column: str = 'Close',
                          add_to_data: bool = False) -> pd.Series:
        """
        Calculate cumulative returns.
        
        Args:
            column: Column name
            add_to_data: If True, adds cumulative returns column to self.data
        
        Returns:
            Series with cumulative returns
        """
        self._validate_column(column)
        
        daily_returns = self.data[column].pct_change()
        cum_returns = (1 + daily_returns).cumprod() - 1
        
        if add_to_data:
            self.data[f'{column}_cumulative_return'] = cum_returns * 100
        
        return cum_returns * 100
    
    # ==================== Volatility ====================
    
    def volatility(self,
                   column: str = 'Close',
                   window: int = 20,
                   annualize: bool = False,
                   add_to_data: bool = False) -> pd.Series:
        """
        Calculate rolling volatility (standard deviation of returns).
        
        Args:
            column: Column name
            window: Rolling window size
            annualize: If True, annualizes volatility (assumes 252 trading days)
            add_to_data: If True, adds volatility column to self.data
        
        Returns:
            Series with volatility values
        
        Example:
            >>> analyzer = StockDataAnalyzer(data)
            >>> vol_20 = analyzer.volatility('Close', window=20)
            >>> annual_vol = analyzer.volatility('Close', window=20, annualize=True)
        """
        self._validate_column(column)
        
        returns = self.data[column].pct_change()
        vol = returns.rolling(window=window).std()
        
        if annualize:
            vol = vol * np.sqrt(252)
        
        if add_to_data:
            suffix = '_annualized' if annualize else ''
            self.data[f'{column}_volatility_{window}{suffix}'] = vol * 100
        
        return vol * 100
    
    # ==================== Range and Spread ====================
    
    def daily_range(self, add_to_data: bool = False) -> pd.Series:
        """
        Calculate daily range (High - Low).
        
        Args:
            add_to_data: If True, adds daily range column to self.data
        
        Returns:
            Series with daily ranges
        """
        if 'High' not in self.data.columns or 'Low' not in self.data.columns:
            raise ValueError("Data must have 'High' and 'Low' columns")
        
        daily_range = self.data['High'] - self.data['Low']
        
        if add_to_data:
            self.data['Daily_Range'] = daily_range
        
        return daily_range
    
    def average_true_range(self, window: int = 14, add_to_data: bool = False) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        Args:
            window: Window size for ATR calculation
            add_to_data: If True, adds ATR column to self.data
        
        Returns:
            Series with ATR values
        """
        required_cols = ['High', 'Low', 'Close']
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"Data must have '{col}' column for ATR calculation")
        
        high_low = self.data['High'] - self.data['Low']
        high_close = np.abs(self.data['High'] - self.data['Close'].shift())
        low_close = np.abs(self.data['Low'] - self.data['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=window).mean()
        
        if add_to_data:
            self.data[f'ATR_{window}'] = atr
        
        return atr
    
    # ==================== Helper Methods ====================
    
    def _validate_column(self, column: str):
        """Validate that column exists in data."""
        if column not in self.data.columns:
            raise ValueError(f"Column '{column}' not found. Available columns: {list(self.data.columns)}")
    
    def get_data(self) -> pd.DataFrame:
        """Get the current data (with any added columns)."""
        return self.data.copy()
    
    def reset_data(self, data: pd.DataFrame):
        """Reset the analyzer with new data."""
        self.__init__(data)
    
    def __repr__(self):
        return f"StockDataAnalyzer(records={len(self.data)}, columns={list(self.data.columns)})"
