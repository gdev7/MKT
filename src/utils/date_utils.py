"""
Date utilities for handling trading days, holidays, and NSE calendar.
"""
from datetime import datetime, timedelta, date
from typing import List, Optional, Union
from src.config import settings


def is_weekend(date_obj: Union[datetime, date]) -> bool:
    """
    Check if a date falls on a weekend.
    
    Args:
        date_obj: Date to check
    
    Returns:
        True if weekend, False otherwise
    """
    return date_obj.weekday() in settings.WEEKEND_DAYS


def is_nse_holiday(date_obj: Union[datetime, date, str]) -> bool:
    """
    Check if a date is an NSE holiday.
    
    Args:
        date_obj: Date to check (datetime, date, or string YYYY-MM-DD)
    
    Returns:
        True if NSE holiday, False otherwise
    """
    if isinstance(date_obj, str):
        date_str = date_obj
    else:
        date_str = date_obj.strftime('%Y-%m-%d')
    
    return date_str in settings.NSE_HOLIDAYS_2025


def is_trading_day(date_obj: Union[datetime, date, str]) -> bool:
    """
    Check if a date is a trading day (not weekend or holiday).
    
    Args:
        date_obj: Date to check
    
    Returns:
        True if trading day, False otherwise
    """
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
    
    return not (is_weekend(date_obj) or is_nse_holiday(date_obj))


def get_next_trading_day(date_obj: Union[datetime, date, str]) -> date:
    """
    Get the next trading day after the given date.
    
    Args:
        date_obj: Starting date
    
    Returns:
        Next trading day
    """
    if isinstance(date_obj, str):
        current = datetime.strptime(date_obj, '%Y-%m-%d').date()
    elif isinstance(date_obj, datetime):
        current = date_obj.date()
    else:
        current = date_obj
    
    current += timedelta(days=1)
    
    while not is_trading_day(current):
        current += timedelta(days=1)
    
    return current


def get_previous_trading_day(date_obj: Union[datetime, date, str]) -> date:
    """
    Get the previous trading day before the given date.
    
    Args:
        date_obj: Starting date
    
    Returns:
        Previous trading day
    """
    if isinstance(date_obj, str):
        current = datetime.strptime(date_obj, '%Y-%m-%d').date()
    elif isinstance(date_obj, datetime):
        current = date_obj.date()
    else:
        current = date_obj
    
    current -= timedelta(days=1)
    
    while not is_trading_day(current):
        current -= timedelta(days=1)
    
    return current


def get_trading_days_between(
    start_date: Union[datetime, date, str],
    end_date: Union[datetime, date, str]
) -> List[date]:
    """
    Get all trading days between two dates (inclusive).
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        List of trading days
    """
    if isinstance(start_date, str):
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
    elif isinstance(start_date, datetime):
        start = start_date.date()
    else:
        start = start_date
    
    if isinstance(end_date, str):
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    elif isinstance(end_date, datetime):
        end = end_date.date()
    else:
        end = end_date
    
    trading_days = []
    current = start
    
    while current <= end:
        if is_trading_day(current):
            trading_days.append(current)
        current += timedelta(days=1)
    
    return trading_days


def count_trading_days(
    start_date: Union[datetime, date, str],
    end_date: Union[datetime, date, str]
) -> int:
    """
    Count the number of trading days between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        Number of trading days
    """
    return len(get_trading_days_between(start_date, end_date))


def add_trading_days(
    start_date: Union[datetime, date, str],
    num_days: int
) -> date:
    """
    Add a specified number of trading days to a date.
    
    Args:
        start_date: Starting date
        num_days: Number of trading days to add (can be negative)
    
    Returns:
        Resulting date
    """
    if isinstance(start_date, str):
        current = datetime.strptime(start_date, '%Y-%m-%d').date()
    elif isinstance(start_date, datetime):
        current = start_date.date()
    else:
        current = start_date
    
    count = 0
    direction = 1 if num_days >= 0 else -1
    target = abs(num_days)
    
    while count < target:
        current += timedelta(days=direction)
        if is_trading_day(current):
            count += 1
    
    return current


def get_quarter_dates(year: int, quarter: int) -> tuple:
    """
    Get start and end dates for a fiscal quarter.
    
    Args:
        year: Year
        quarter: Quarter number (1-4)
    
    Returns:
        Tuple of (start_date, end_date)
    """
    quarter_map = {
        1: (1, 1, 3, 31),    # Q1: Jan-Mar
        2: (4, 1, 6, 30),    # Q2: Apr-Jun
        3: (7, 1, 9, 30),    # Q3: Jul-Sep
        4: (10, 1, 12, 31),  # Q4: Oct-Dec
    }
    
    if quarter not in quarter_map:
        raise ValueError("Quarter must be 1, 2, 3, or 4")
    
    start_month, start_day, end_month, end_day = quarter_map[quarter]
    start_date = date(year, start_month, start_day)
    end_date = date(year, end_month, end_day)
    
    return start_date, end_date


def validate_date_range(
    start_date: Optional[str],
    end_date: Optional[str]
) -> tuple:
    """
    Validate and parse date range strings.
    
    Args:
        start_date: Start date string (YYYY-MM-DD) or None
        end_date: End date string (YYYY-MM-DD) or None
    
    Returns:
        Tuple of (start_date_obj, end_date_obj) or (None, None)
    
    Raises:
        ValueError: If date format is invalid or range is invalid
    """
    start_obj = None
    end_obj = None
    
    if start_date:
        try:
            start_obj = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid start date format: {start_date}. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end_obj = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid end date format: {end_date}. Use YYYY-MM-DD")
    
    if start_obj and end_obj and start_obj > end_obj:
        raise ValueError("Start date must be before end date")
    
    return start_obj, end_obj


def get_market_status(dt: Optional[datetime] = None) -> str:
    """
    Get current NSE market status.
    
    Args:
        dt: Datetime to check (default: current time)
    
    Returns:
        Market status string: 'pre_open', 'open', 'closed', or 'holiday'
    """
    if dt is None:
        dt = datetime.now()
    
    # Check if holiday or weekend
    if not is_trading_day(dt):
        return 'holiday'
    
    # Get current time
    current_time = dt.time()
    
    # Parse trading hours
    pre_open_start = datetime.strptime(settings.TRADING_HOURS['pre_open_start'], '%H:%M').time()
    market_open = datetime.strptime(settings.TRADING_HOURS['market_open'], '%H:%M').time()
    market_close = datetime.strptime(settings.TRADING_HOURS['market_close'], '%H:%M').time()
    
    if pre_open_start <= current_time < market_open:
        return 'pre_open'
    elif market_open <= current_time < market_close:
        return 'open'
    else:
        return 'closed'


def get_fiscal_year(dt: Union[datetime, date, str]) -> int:
    """
    Get the Indian fiscal year for a given date.
    Indian fiscal year runs from April 1 to March 31.
    
    Args:
        dt: Date to check
    
    Returns:
        Fiscal year (e.g., 2024 for FY 2024-25)
    """
    if isinstance(dt, str):
        dt = datetime.strptime(dt, '%Y-%m-%d')
    
    if isinstance(dt, datetime):
        dt = dt.date()
    
    # If month is Jan-Mar, fiscal year is previous calendar year
    if dt.month < 4:
        return dt.year - 1
    else:
        return dt.year
