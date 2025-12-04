"""
Stock Data Reader Module

This module provides comprehensive data access functionality for stock CSV files.
Supports various filtering options including date ranges, lookback periods, and time-based queries.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Union, Tuple
import warnings

warnings.filterwarnings('ignore')


class StockDataReader:
    """
    A comprehensive data reader for stock CSV files with advanced filtering capabilities.
    
    Features:
    - Load complete or partial CSV data
    - Filter by date ranges
    - Get data from specific dates
    - Retrieve data with lookback periods
    - Query by year/quarter/month/week
    """
    
    def __init__(self, csv_path: Union[str, Path]):
        """
        Initialize the StockDataReader.
        
        Args:
            csv_path: Path to the stock CSV file
        """
        self.csv_path = Path(csv_path)
        self.symbol = self.csv_path.stem
        self._data = None
        self._load_data()
    
    def _load_data(self):
        """Load and preprocess the CSV data."""
        try:
            # Read CSV - Row 1 has column names (Price, Close, High, Low, Open, Volume)
            # Row 2 has ticker info, Row 3 is empty/header, data starts from Row 4
            # The "Price" column actually contains dates
            
            # Read the header to get column names
            header_df = pd.read_csv(self.csv_path, nrows=1)
            column_names = header_df.columns.tolist()
            
            # Read the actual data starting from row 3 (0-indexed)
            df = pd.read_csv(self.csv_path, skiprows=3, names=column_names)
            
            # Rename 'Price' column to 'Date' since it contains dates
            if 'Price' in df.columns:
                df = df.rename(columns={'Price': 'Date'})
            
            # Convert Date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Sort by date
            df = df.sort_values('Date').reset_index(drop=True)
            
            # Convert numeric columns
            numeric_cols = ['Close', 'High', 'Low', 'Open', 'Volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            self._data = df
            
        except Exception as e:
            raise ValueError(f"Error loading CSV file {self.csv_path}: {str(e)}")
    
    @property
    def data(self) -> pd.DataFrame:
        """Get the complete dataframe."""
        return self._data.copy()
    
    def get_columns(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get complete CSV data with all or specific columns.
        
        Args:
            columns: List of column names to retrieve. If None, returns all columns.
        
        Returns:
            DataFrame with requested columns
        
        Example:
            >>> reader = StockDataReader('3MINDIA.csv')
            >>> # Get all columns
            >>> all_data = reader.get_columns()
            >>> # Get specific columns
            >>> price_data = reader.get_columns(['Date', 'Close', 'Volume'])
        """
        if columns is None:
            return self._data.copy()
        
        # Validate columns
        invalid_cols = [col for col in columns if col not in self._data.columns]
        if invalid_cols:
            raise ValueError(f"Invalid columns: {invalid_cols}. Available: {list(self._data.columns)}")
        
        return self._data[columns].copy()
    
    def get_date_range(self, 
                       start_date: Optional[Union[str, datetime]] = None,
                       end_date: Optional[Union[str, datetime]] = None,
                       columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get data for a range of dates.
        
        Args:
            start_date: Start date (inclusive). Format: 'YYYY-MM-DD' or datetime object
            end_date: End date (inclusive). Format: 'YYYY-MM-DD' or datetime object
            columns: List of column names to retrieve
        
        Returns:
            DataFrame filtered by date range
        
        Example:
            >>> reader = StockDataReader('3MINDIA.csv')
            >>> data = reader.get_date_range('2024-01-01', '2024-12-31')
            >>> data = reader.get_date_range('2024-01-01', columns=['Date', 'Close'])
        """
        df = self.get_columns(columns)
        
        # Convert dates to datetime
        if start_date:
            start_date = pd.to_datetime(start_date)
            df = df[df['Date'] >= start_date]
        
        if end_date:
            end_date = pd.to_datetime(end_date)
            df = df[df['Date'] <= end_date]
        
        return df.reset_index(drop=True)
    
    def get_from_date(self, 
                      from_date: Union[str, datetime],
                      columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get data from a particular date onwards.
        
        Args:
            from_date: Starting date (inclusive). Format: 'YYYY-MM-DD' or datetime object
            columns: List of column names to retrieve
        
        Returns:
            DataFrame from the specified date onwards
        
        Example:
            >>> reader = StockDataReader('3MINDIA.csv')
            >>> data = reader.get_from_date('2024-01-01')
        """
        return self.get_date_range(start_date=from_date, end_date=None, columns=columns)
    
    def get_on_date(self,
                    date: Union[str, datetime],
                    columns: Optional[List[str]] = None) -> pd.Series:
        """
        Get data for a specific date.
        
        Args:
            date: Specific date. Format: 'YYYY-MM-DD' or datetime object
            columns: List of column names to retrieve
        
        Returns:
            Series with data for the specific date
        
        Example:
            >>> reader = StockDataReader('3MINDIA.csv')
            >>> data = reader.get_on_date('2024-01-15')
        """
        date = pd.to_datetime(date)
        df = self.get_columns(columns)
        
        result = df[df['Date'] == date]
        
        if result.empty:
            # Try to find the nearest date
            nearest_idx = (df['Date'] - date).abs().idxmin()
            warnings.warn(f"Exact date {date.date()} not found. Returning nearest date: {df.loc[nearest_idx, 'Date'].date()}")
            return df.loc[nearest_idx]
        
        return result.iloc[0]
    
    def get_lookback(self,
                     from_date: Union[str, datetime],
                     days: int = 10,
                     columns: Optional[List[str]] = None,
                     include_from_date: bool = True) -> pd.DataFrame:
        """
        Get data from a particular date and the previous N days.
        
        Args:
            from_date: Reference date. Format: 'YYYY-MM-DD' or datetime object
            days: Number of previous days to include (default: 10)
            columns: List of column names to retrieve
            include_from_date: Whether to include the from_date in results
        
        Returns:
            DataFrame with data for the specified lookback period
        
        Example:
            >>> reader = StockDataReader('3MINDIA.csv')
            >>> # Get data for a date and previous 10 days
            >>> data = reader.get_lookback('2024-01-15', days=10)
            >>> # Get previous 30 days
            >>> data = reader.get_lookback('2024-01-15', days=30)
        """
        from_date = pd.to_datetime(from_date)
        df = self.get_columns(columns)
        
        # Filter data up to from_date
        if include_from_date:
            df_filtered = df[df['Date'] <= from_date]
        else:
            df_filtered = df[df['Date'] < from_date]
        
        # Get last N rows (trading days, not calendar days)
        result = df_filtered.tail(days + (1 if include_from_date else 0))
        
        return result.reset_index(drop=True)
    
    def get_by_year(self,
                    year: Union[int, List[int], str] = 'all',
                    columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get data for specific year(s) or all years.
        
        Args:
            year: Year(s) to retrieve. Can be:
                  - Single year: 2024
                  - List of years: [2023, 2024]
                  - 'all': All years
            columns: List of column names to retrieve
        
        Returns:
            DataFrame filtered by year
        
        Example:
            >>> reader = StockDataReader('3MINDIA.csv')
            >>> # Get data for 2024
            >>> data_2024 = reader.get_by_year(2024)
            >>> # Get data for multiple years
            >>> data = reader.get_by_year([2023, 2024])
            >>> # Get all years
            >>> all_data = reader.get_by_year('all')
        """
        df = self.get_columns(columns)
        
        if year == 'all':
            return df
        
        df['Year'] = df['Date'].dt.year
        
        if isinstance(year, int):
            result = df[df['Year'] == year]
        elif isinstance(year, list):
            result = df[df['Year'].isin(year)]
        else:
            raise ValueError(f"Invalid year parameter: {year}")
        
        return result.drop('Year', axis=1).reset_index(drop=True)
    
    def get_by_quarter(self,
                       year: int,
                       quarter: Union[int, List[int], str] = 'all',
                       columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get data for specific quarter(s) of a year.
        
        Args:
            year: Year to query
            quarter: Quarter(s) to retrieve (1-4). Can be:
                    - Single quarter: 1
                    - List of quarters: [1, 2]
                    - 'all': All quarters
            columns: List of column names to retrieve
        
        Returns:
            DataFrame filtered by quarter
        
        Example:
            >>> reader = StockDataReader('3MINDIA.csv')
            >>> # Get Q1 2024 data
            >>> q1_data = reader.get_by_quarter(2024, 1)
            >>> # Get Q1 and Q2 2024
            >>> data = reader.get_by_quarter(2024, [1, 2])
        """
        df = self.get_by_year(year, columns)
        
        if quarter == 'all':
            return df
        
        df['Quarter'] = df['Date'].dt.quarter
        
        if isinstance(quarter, int):
            if quarter not in [1, 2, 3, 4]:
                raise ValueError(f"Quarter must be 1-4, got {quarter}")
            result = df[df['Quarter'] == quarter]
        elif isinstance(quarter, list):
            if not all(q in [1, 2, 3, 4] for q in quarter):
                raise ValueError(f"All quarters must be 1-4")
            result = df[df['Quarter'].isin(quarter)]
        else:
            raise ValueError(f"Invalid quarter parameter: {quarter}")
        
        return result.drop('Quarter', axis=1).reset_index(drop=True)
    
    def get_by_month(self,
                     year: int,
                     month: Union[int, List[int], str] = 'all',
                     columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get data for specific month(s) of a year.
        
        Args:
            year: Year to query
            month: Month(s) to retrieve (1-12). Can be:
                  - Single month: 1
                  - List of months: [1, 2, 3]
                  - 'all': All months
            columns: List of column names to retrieve
        
        Returns:
            DataFrame filtered by month
        
        Example:
            >>> reader = StockDataReader('3MINDIA.csv')
            >>> # Get January 2024 data
            >>> jan_data = reader.get_by_month(2024, 1)
            >>> # Get Jan-Mar 2024
            >>> data = reader.get_by_month(2024, [1, 2, 3])
        """
        df = self.get_by_year(year, columns)
        
        if month == 'all':
            return df
        
        df['Month'] = df['Date'].dt.month
        
        if isinstance(month, int):
            if month not in range(1, 13):
                raise ValueError(f"Month must be 1-12, got {month}")
            result = df[df['Month'] == month]
        elif isinstance(month, list):
            if not all(m in range(1, 13) for m in month):
                raise ValueError(f"All months must be 1-12")
            result = df[df['Month'].isin(month)]
        else:
            raise ValueError(f"Invalid month parameter: {month}")
        
        return result.drop('Month', axis=1).reset_index(drop=True)
    
    def get_by_week(self,
                    year: int,
                    week: Union[int, List[int], str] = 'all',
                    columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get data for specific week(s) of a year (ISO week number).
        
        Args:
            year: Year to query
            week: Week(s) to retrieve (1-53). Can be:
                 - Single week: 1
                 - List of weeks: [1, 2, 3]
                 - 'all': All weeks
            columns: List of column names to retrieve
        
        Returns:
            DataFrame filtered by week
        
        Example:
            >>> reader = StockDataReader('3MINDIA.csv')
            >>> # Get week 1 of 2024
            >>> week1_data = reader.get_by_week(2024, 1)
            >>> # Get first 4 weeks of 2024
            >>> data = reader.get_by_week(2024, [1, 2, 3, 4])
        """
        df = self.get_by_year(year, columns)
        
        if week == 'all':
            return df
        
        df['Week'] = df['Date'].dt.isocalendar().week
        
        if isinstance(week, int):
            if week not in range(1, 54):
                raise ValueError(f"Week must be 1-53, got {week}")
            result = df[df['Week'] == week]
        elif isinstance(week, list):
            if not all(w in range(1, 54) for w in week):
                raise ValueError(f"All weeks must be 1-53")
            result = df[df['Week'].isin(week)]
        else:
            raise ValueError(f"Invalid week parameter: {week}")
        
        return result.drop('Week', axis=1).reset_index(drop=True)
    
    def get_info(self) -> dict:
        """
        Get summary information about the stock data.
        
        Returns:
            Dictionary with data statistics
        """
        return {
            'symbol': self.symbol,
            'total_records': len(self._data),
            'date_range': {
                'start': self._data['Date'].min().strftime('%Y-%m-%d'),
                'end': self._data['Date'].max().strftime('%Y-%m-%d')
            },
            'years_available': sorted(self._data['Date'].dt.year.unique().tolist()),
            'columns': list(self._data.columns)
        }
    
    def __repr__(self):
        info = self.get_info()
        return (f"StockDataReader(symbol='{info['symbol']}', "
                f"records={info['total_records']}, "
                f"date_range='{info['date_range']['start']} to {info['date_range']['end']}')")
