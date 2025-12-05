"""
Base strategy class for implementing trading strategies.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.exceptions import StrategyError
from src.utils.constants import TradeSide, PositionType

logger = get_logger(__name__)


class Signal:
    """Represents a trading signal."""
    
    def __init__(
        self,
        date: datetime,
        symbol: str,
        side: TradeSide,
        price: float,
        quantity: int = 0,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a trading signal.
        
        Args:
            date: Signal date
            symbol: Stock symbol
            side: Buy or Sell
            price: Signal price
            quantity: Number of shares (0 for automatic sizing)
            confidence: Signal confidence (0-1)
            metadata: Additional signal metadata
        """
        self.date = date
        self.symbol = symbol
        self.side = side
        self.price = price
        self.quantity = quantity
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def __repr__(self) -> str:
        return (f"Signal({self.date.strftime('%Y-%m-%d')}, {self.symbol}, "
                f"{self.side.value}, {self.price}, qty={self.quantity})")


class Position:
    """Represents an open position."""
    
    def __init__(
        self,
        symbol: str,
        entry_date: datetime,
        entry_price: float,
        quantity: int,
        position_type: PositionType = PositionType.LONG
    ):
        """
        Initialize a position.
        
        Args:
            symbol: Stock symbol
            entry_date: Entry date
            entry_price: Entry price
            quantity: Number of shares
            position_type: Long or Short
        """
        self.symbol = symbol
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.quantity = quantity
        self.position_type = position_type
        self.exit_date: Optional[datetime] = None
        self.exit_price: Optional[float] = None
    
    def close(self, exit_date: datetime, exit_price: float) -> None:
        """Close the position."""
        self.exit_date = exit_date
        self.exit_price = exit_price
    
    def get_return(self) -> float:
        """
        Calculate position return.
        
        Returns:
            Return as a decimal (e.g., 0.05 for 5%)
        """
        if self.exit_price is None:
            return 0.0
        
        if self.position_type == PositionType.LONG:
            return (self.exit_price - self.entry_price) / self.entry_price
        else:  # SHORT
            return (self.entry_price - self.exit_price) / self.entry_price
    
    def get_pnl(self) -> float:
        """Calculate profit/loss in absolute terms."""
        return self.get_return() * self.entry_price * self.quantity
    
    def __repr__(self) -> str:
        status = "OPEN" if self.exit_price is None else "CLOSED"
        return (f"Position({self.symbol}, {status}, "
                f"entry={self.entry_price}, qty={self.quantity})")


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    Subclasses must implement:
    - initialize(): Setup strategy parameters
    - generate_signals(): Generate trading signals from data
    """
    
    def __init__(self, name: str = "BaseStrategy"):
        """
        Initialize the strategy.
        
        Args:
            name: Strategy name
        """
        self.name = name
        self.logger = get_logger(f"{__name__}.{name}")
        self.parameters: Dict[str, Any] = {}
        self.positions: List[Position] = []
        self.signals: List[Signal] = []
    
    @abstractmethod
    def initialize(self, **kwargs) -> None:
        """
        Initialize strategy parameters.
        
        This method should set up all strategy-specific parameters.
        
        Args:
            **kwargs: Strategy parameters
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals from historical data.
        
        Args:
            data: DataFrame with OHLCV data and DATE column
        
        Returns:
            List of Signal objects
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> None:
        """
        Validate input data format.
        
        Args:
            data: Input dataframe
        
        Raises:
            StrategyError: If data format is invalid
        """
        required_cols = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            raise StrategyError(f"Missing required columns: {missing_cols}")
        
        if len(data) == 0:
            raise StrategyError("Data is empty")
    
    def set_parameters(self, **kwargs) -> None:
        """
        Set strategy parameters.
        
        Args:
            **kwargs: Parameter key-value pairs
        """
        self.parameters.update(kwargs)
        self.logger.info(f"Updated parameters: {kwargs}")
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get current strategy parameters.
        
        Returns:
            Dictionary of parameters
        """
        return self.parameters.copy()
    
    def reset(self) -> None:
        """Reset strategy state."""
        self.positions = []
        self.signals = []
        self.logger.info(f"Strategy {self.name} reset")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get basic strategy statistics.
        
        Returns:
            Dictionary with strategy stats
        """
        closed_positions = [p for p in self.positions if p.exit_price is not None]
        
        if not closed_positions:
            return {
                'total_signals': len(self.signals),
                'total_positions': len(self.positions),
                'closed_positions': 0,
                'win_rate': 0.0,
                'avg_return': 0.0,
            }
        
        returns = [p.get_return() for p in closed_positions]
        wins = [r for r in returns if r > 0]
        
        return {
            'total_signals': len(self.signals),
            'total_positions': len(self.positions),
            'closed_positions': len(closed_positions),
            'win_rate': len(wins) / len(closed_positions) if closed_positions else 0.0,
            'avg_return': sum(returns) / len(returns) if returns else 0.0,
            'max_return': max(returns) if returns else 0.0,
            'min_return': min(returns) if returns else 0.0,
        }
    
    def __repr__(self) -> str:
        return f"{self.name}(signals={len(self.signals)}, positions={len(self.positions)})"
