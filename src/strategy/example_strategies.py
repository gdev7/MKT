"""
Example trading strategies demonstrating the strategy framework.
"""
import pandas as pd
import numpy as np
from typing import List
from src.strategy.base_strategy import BaseStrategy, Signal
from src.utils.constants import TradeSide
from src.config import settings


class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    Simple moving average crossover strategy.
    
    Buy when fast MA crosses above slow MA.
    Sell when fast MA crosses below slow MA.
    """
    
    def __init__(self):
        """Initialize the strategy."""
        super().__init__(name="MA Crossover")
    
    def initialize(self, fast_period: int = 20, slow_period: int = 50, **kwargs) -> None:
        """
        Initialize strategy parameters.
        
        Args:
            fast_period: Fast moving average period
            slow_period: Slow moving average period
        """
        self.parameters = {
            'fast_period': fast_period,
            'slow_period': slow_period
        }
        self.logger.info(f"Initialized with fast={fast_period}, slow={slow_period}")
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals based on MA crossover.
        
        Args:
            data: DataFrame with OHLCV data and DATE column
        
        Returns:
            List of trading signals
        """
        self.validate_data(data)
        
        df = data.copy()
        
        # Calculate moving averages
        fast_period = self.parameters.get('fast_period', 20)
        slow_period = self.parameters.get('slow_period', 50)
        
        df['MA_FAST'] = df['CLOSE'].rolling(window=fast_period).mean()
        df['MA_SLOW'] = df['CLOSE'].rolling(window=slow_period).mean()
        
        # Generate signals
        signals = []
        
        for i in range(1, len(df)):
            prev_fast = df.iloc[i-1]['MA_FAST']
            prev_slow = df.iloc[i-1]['MA_SLOW']
            curr_fast = df.iloc[i]['MA_FAST']
            curr_slow = df.iloc[i]['MA_SLOW']
            
            # Skip if MAs not calculated yet
            if pd.isna(prev_fast) or pd.isna(curr_fast):
                continue
            
            # Buy signal: Fast MA crosses above Slow MA
            if prev_fast <= prev_slow and curr_fast > curr_slow:
                signal = Signal(
                    date=df.iloc[i]['DATE'],
                    symbol='STOCK',
                    side=TradeSide.BUY,
                    price=df.iloc[i]['CLOSE'],
                    metadata={'fast_ma': curr_fast, 'slow_ma': curr_slow}
                )
                signals.append(signal)
                self.logger.debug(f"BUY signal at {signal.date}: {signal.price:.2f}")
            
            # Sell signal: Fast MA crosses below Slow MA
            elif prev_fast >= prev_slow and curr_fast < curr_slow:
                signal = Signal(
                    date=df.iloc[i]['DATE'],
                    symbol='STOCK',
                    side=TradeSide.SELL,
                    price=df.iloc[i]['CLOSE'],
                    metadata={'fast_ma': curr_fast, 'slow_ma': curr_slow}
                )
                signals.append(signal)
                self.logger.debug(f"SELL signal at {signal.date}: {signal.price:.2f}")
        
        self.signals = signals
        self.logger.info(f"Generated {len(signals)} signals")
        
        return signals


class RSIStrategy(BaseStrategy):
    """
    RSI-based mean reversion strategy.
    
    Buy when RSI < oversold threshold.
    Sell when RSI > overbought threshold.
    """
    
    def __init__(self):
        """Initialize the strategy."""
        super().__init__(name="RSI Strategy")
    
    def initialize(
        self,
        rsi_period: int = 14,
        oversold: int = 30,
        overbought: int = 70,
        **kwargs
    ) -> None:
        """
        Initialize strategy parameters.
        
        Args:
            rsi_period: RSI calculation period
            oversold: Oversold threshold
            overbought: Overbought threshold
        """
        self.parameters = {
            'rsi_period': rsi_period,
            'oversold': oversold,
            'overbought': overbought
        }
        self.logger.info(f"Initialized with RSI={rsi_period}, "
                        f"oversold={oversold}, overbought={overbought}")
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals based on RSI.
        
        Args:
            data: DataFrame with OHLCV data and DATE column
        
        Returns:
            List of trading signals
        """
        self.validate_data(data)
        
        df = data.copy()
        
        # Calculate RSI
        rsi_period = self.parameters.get('rsi_period', 14)
        oversold = self.parameters.get('oversold', 30)
        overbought = self.parameters.get('overbought', 70)
        
        df['RSI'] = self._calculate_rsi(df['CLOSE'], rsi_period)
        
        # Generate signals
        signals = []
        in_position = False
        
        for i in range(1, len(df)):
            rsi = df.iloc[i]['RSI']
            
            if pd.isna(rsi):
                continue
            
            # Buy signal: RSI crosses below oversold
            if not in_position and rsi < oversold:
                signal = Signal(
                    date=df.iloc[i]['DATE'],
                    symbol='STOCK',
                    side=TradeSide.BUY,
                    price=df.iloc[i]['CLOSE'],
                    confidence=(oversold - rsi) / oversold,
                    metadata={'rsi': rsi}
                )
                signals.append(signal)
                in_position = True
                self.logger.debug(f"BUY signal at {signal.date}: RSI={rsi:.2f}")
            
            # Sell signal: RSI crosses above overbought
            elif in_position and rsi > overbought:
                signal = Signal(
                    date=df.iloc[i]['DATE'],
                    symbol='STOCK',
                    side=TradeSide.SELL,
                    price=df.iloc[i]['CLOSE'],
                    confidence=(rsi - overbought) / (100 - overbought),
                    metadata={'rsi': rsi}
                )
                signals.append(signal)
                in_position = False
                self.logger.debug(f"SELL signal at {signal.date}: RSI={rsi:.2f}")
        
        self.signals = signals
        self.logger.info(f"Generated {len(signals)} signals")
        
        return signals
