"""
Backtesting engine for testing trading strategies.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.strategy.base_strategy import BaseStrategy, Signal, Position
from src.strategy.metrics import PerformanceMetrics
from src.utils.logger import get_logger
from src.utils.exceptions import BacktestError
from src.utils.constants import TradeSide, PositionType
from src.config import settings

logger = get_logger(__name__)


class Backtester:
    """
    Backtesting engine for evaluating trading strategies.
    
    Supports single-stock and portfolio backtesting with:
    - Position sizing
    - Commission and slippage
    - Risk management
    - Performance metrics calculation
    """
    
    def __init__(
        self,
        initial_capital: float = None,
        commission: float = None,
        slippage: float = None,
        position_size: float = None
    ):
        """
        Initialize the backtester.
        
        Args:
            initial_capital: Starting capital (default from settings)
            commission: Commission per trade as decimal (default from settings)
            slippage: Slippage as decimal (default from settings)
            position_size: Position size as fraction of portfolio (default from settings)
        """
        self.initial_capital = initial_capital or settings.BACKTESTING_DEFAULTS['initial_capital']
        self.commission = commission or settings.BACKTESTING_DEFAULTS['commission']
        self.slippage = slippage or settings.BACKTESTING_DEFAULTS['slippage']
        self.position_size = position_size or settings.BACKTESTING_DEFAULTS['position_size']
        
        self.logger = get_logger(__name__)
        
        # State variables
        self.cash = self.initial_capital
        self.positions: List[Position] = []
        self.closed_positions: List[Position] = []
        self.equity_curve: pd.Series = pd.Series(dtype=float)
        self.trades: List[Dict[str, Any]] = []
    
    def run(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        symbol: str = "UNKNOWN"
    ) -> Dict[str, Any]:
        """
        Run backtest on a single stock.
        
        Args:
            strategy: Trading strategy to test
            data: OHLCV data with DATE column
            symbol: Stock symbol
        
        Returns:
            Dictionary with backtest results and metrics
        """
        self.logger.info(f"Starting backtest for {symbol} with {strategy.name}")
        
        # Reset state
        self._reset()
        
        # Validate data
        strategy.validate_data(data)
        
        # Generate signals
        signals = strategy.generate_signals(data)
        self.logger.info(f"Generated {len(signals)} signals")
        
        if not signals:
            self.logger.warning("No signals generated")
            return self._get_results()
        
        # Process signals chronologically
        data_indexed = data.set_index('DATE').sort_index()
        
        for signal in sorted(signals, key=lambda s: s.date):
            self._process_signal(signal, data_indexed, symbol)
        
        # Close any remaining positions at end
        if self.positions:
            last_date = data_indexed.index[-1]
            last_price = data_indexed.loc[last_date, 'CLOSE']
            
            for pos in self.positions:
                self._close_position(pos, last_date, last_price)
        
        # Calculate final metrics
        results = self._get_results()
        
        self.logger.info(f"Backtest complete. Total return: {results['metrics']['total_return']*100:.2f}%")
        
        return results
    
    def _reset(self) -> None:
        """Reset backtester state."""
        self.cash = self.initial_capital
        self.positions = []
        self.closed_positions = []
        self.equity_curve = pd.Series(dtype=float)
        self.trades = []
    
    def _process_signal(
        self,
        signal: Signal,
        data: pd.DataFrame,
        symbol: str
    ) -> None:
        """
        Process a trading signal.
        
        Args:
            signal: Trading signal
            data: Price data indexed by date
            symbol: Stock symbol
        """
        if signal.date not in data.index:
            self.logger.warning(f"Signal date {signal.date} not in data, skipping")
            return
        
        # Get execution price with slippage
        base_price = signal.price
        
        if signal.side == TradeSide.BUY:
            execution_price = base_price * (1 + self.slippage)
            self._open_position(signal, execution_price, symbol)
        else:  # SELL
            execution_price = base_price * (1 - self.slippage)
            self._close_positions_for_signal(signal, execution_price)
    
    def _open_position(
        self,
        signal: Signal,
        execution_price: float,
        symbol: str
    ) -> None:
        """
        Open a new position.
        
        Args:
            signal: Buy signal
            execution_price: Execution price with slippage
            symbol: Stock symbol
        """
        # Calculate position size
        position_value = self.cash * self.position_size
        
        if signal.quantity > 0:
            quantity = signal.quantity
        else:
            quantity = int(position_value / execution_price)
        
        if quantity == 0:
            self.logger.warning(f"Insufficient funds for position at {execution_price}")
            return
        
        # Calculate costs
        trade_value = quantity * execution_price
        commission_cost = trade_value * self.commission
        total_cost = trade_value + commission_cost
        
        if total_cost > self.cash:
            # Reduce quantity to fit available cash
            max_quantity = int(self.cash / (execution_price * (1 + self.commission)))
            if max_quantity == 0:
                self.logger.warning("Insufficient funds for position")
                return
            quantity = max_quantity
            trade_value = quantity * execution_price
            commission_cost = trade_value * self.commission
            total_cost = trade_value + commission_cost
        
        # Update cash
        self.cash -= total_cost
        
        # Create position
        position = Position(
            symbol=symbol,
            entry_date=signal.date,
            entry_price=execution_price,
            quantity=quantity,
            position_type=PositionType.LONG
        )
        
        self.positions.append(position)
        
        self.logger.debug(f"Opened position: {quantity} shares at {execution_price}, "
                         f"cost: {total_cost:.2f}, remaining cash: {self.cash:.2f}")
    
    def _close_positions_for_signal(
        self,
        signal: Signal,
        execution_price: float
    ) -> None:
        """
        Close positions based on sell signal.
        
        Args:
            signal: Sell signal
            execution_price: Execution price with slippage
        """
        if not self.positions:
            return
        
        # Close all positions for the symbol (FIFO)
        positions_to_close = [p for p in self.positions if p.symbol == signal.symbol]
        
        for position in positions_to_close:
            self._close_position(position, signal.date, execution_price)
    
    def _close_position(
        self,
        position: Position,
        exit_date: datetime,
        exit_price: float
    ) -> None:
        """
        Close a position.
        
        Args:
            position: Position to close
            exit_date: Exit date
            exit_price: Exit price
        """
        position.close(exit_date, exit_price)
        
        # Calculate proceeds
        trade_value = position.quantity * exit_price
        commission_cost = trade_value * self.commission
        proceeds = trade_value - commission_cost
        
        # Update cash
        self.cash += proceeds
        
        # Record trade
        pnl = position.get_pnl() - (trade_value * self.commission * 2)  # Entry + exit commission
        
        trade = {
            'symbol': position.symbol,
            'entry_date': position.entry_date,
            'exit_date': exit_date,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'quantity': position.quantity,
            'return': position.get_return(),
            'pnl': pnl,
            'duration': (exit_date - position.entry_date).days
        }
        
        self.trades.append(trade)
        
        # Move to closed positions
        self.positions.remove(position)
        self.closed_positions.append(position)
        
        self.logger.debug(f"Closed position: {position.symbol}, PnL: {pnl:.2f}, "
                         f"return: {position.get_return()*100:.2f}%")
    
    def _get_results(self) -> Dict[str, Any]:
        """
        Get backtest results with metrics.
        
        Returns:
            Dictionary with results
        """
        # Build equity curve
        equity_curve = self._build_equity_curve()
        
        # Calculate metrics
        metrics_calc = PerformanceMetrics()
        metrics = metrics_calc.calculate_all_metrics(
            equity_curve,
            self.trades,
            self.initial_capital
        )
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': self.cash + self._get_positions_value(),
            'cash': self.cash,
            'positions': len(self.positions),
            'closed_positions': len(self.closed_positions),
            'equity_curve': equity_curve,
            'trades': self.trades,
            'metrics': metrics
        }
    
    def _build_equity_curve(self) -> pd.Series:
        """
        Build equity curve from trades.
        
        Returns:
            Series of portfolio values indexed by date
        """
        if not self.trades:
            return pd.Series([self.initial_capital], index=[datetime.now()])
        
        # Create daily equity curve
        dates = []
        values = []
        
        # Get all unique dates
        all_dates = set()
        for trade in self.trades:
            all_dates.add(trade['entry_date'])
            all_dates.add(trade['exit_date'])
        
        all_dates = sorted(all_dates)
        
        # Calculate equity at each date
        for date in all_dates:
            equity = self._calculate_equity_at_date(date)
            dates.append(date)
            values.append(equity)
        
        return pd.Series(values, index=dates)
    
    def _calculate_equity_at_date(self, date: datetime) -> float:
        """
        Calculate total equity at a specific date.
        
        Args:
            date: Date to calculate equity
        
        Returns:
            Total equity value
        """
        # Start with cash from closed positions
        cash = self.initial_capital
        
        # Add PnL from closed trades before this date
        for trade in self.trades:
            if trade['exit_date'] <= date:
                cash += trade['pnl']
        
        # Add value of open positions
        # (simplified - uses exit price as current price)
        for pos in self.closed_positions:
            if pos.entry_date <= date < pos.exit_date:
                # Position was open at this date
                # In real implementation, would need price data for this date
                pass
        
        return cash
    
    def _get_positions_value(self) -> float:
        """Get current value of open positions."""
        # Note: This is simplified. In production, would need current prices
        return sum(p.entry_price * p.quantity for p in self.positions)
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """
        Print backtest results.
        
        Args:
            results: Results dictionary from run()
        """
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        
        print(f"\n💰 Capital:")
        print(f"  Initial:  ₹{results['initial_capital']:>12,.2f}")
        print(f"  Final:    ₹{results['final_value']:>12,.2f}")
        print(f"  Cash:     ₹{results['cash']:>12,.2f}")
        
        print(f"\n📊 Positions:")
        print(f"  Open:     {results['positions']:>12}")
        print(f"  Closed:   {results['closed_positions']:>12}")
        
        # Print metrics
        metrics_calc = PerformanceMetrics()
        metrics_calc.print_metrics(results['metrics'])
