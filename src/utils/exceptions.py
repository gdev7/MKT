"""
Custom exceptions for the MKT stock analysis tool.
"""


class MKTError(Exception):
    """Base exception class for MKT application."""
    pass


class DataNotFoundError(MKTError):
    """Raised when requested data is not found."""
    pass


class InvalidSymbolError(MKTError):
    """Raised when an invalid stock symbol is provided."""
    pass


class InvalidDateRangeError(MKTError):
    """Raised when an invalid date range is specified."""
    pass


class DataFetchError(MKTError):
    """Raised when data fetching from external source fails."""
    pass


class MetadataSyncError(MKTError):
    """Raised when metadata synchronization fails."""
    pass


class AnalysisError(MKTError):
    """Raised when analysis computation fails."""
    pass


class ValidationError(MKTError):
    """Raised when data validation fails."""
    pass


class ConfigurationError(MKTError):
    """Raised when configuration is invalid or missing."""
    pass


class BacktestError(MKTError):
    """Raised when backtesting encounters an error."""
    pass


class StrategyError(MKTError):
    """Raised when strategy execution fails."""
    pass
