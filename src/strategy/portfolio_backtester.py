"""
Portfolio Backtester - Test strategies with realistic portfolio constraints.

This module provides a complete backtesting framework for testing trading strategies
with realistic portfolio management, position sizing, and trade limits.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.strategy.base_strategy import BaseStrategy, Signal, Position, TradeAction
from src.utils.logger import get_logger
from src.utils.date_utils import is_trading_day, get_next_trading_day

logger = get_logger(__name__)


class PositionSizing(Enum):
    """Position sizing methods."""
    FIXED_AMOUNT = "fixed_amount"  # Fixed rupee amount per position
    EQUAL_WEIGHT = "equal_weight"  # Equal weight across positions
    PERCENTAGE = "percentage"  # Percentage of portfolio


@dataclass
class PortfolioConfig:
    """Portfolio configuration for backtesting."""
    
    # Capital allocation
    initial_capital: float = 1000000.0  # 10 Lakhs
    position_size_method: PositionSizing = PositionSizing.FIXED_AMOUNT
    position_size_value: float = 100000.0  # 1 Lakh per position
    
    # Trade limits
    max_trades_per_week: int = 5
    max_trades_per_month: int = 20
    max_positions: int = 10  # Maximum concurrent positions
    
    # Risk management
    max_position_size_pct: float = 0.20  # Max 20% per position
    reserve_cash_pct: float = 0.10  # Keep 10% cash reserve
    
    # Trading costs
    brokerage_pct: float = 0.0003  # 0.03% brokerage
    transaction_charges_pct: float = 0.0003  # 0.03% charges
    stt_pct: float = 0.001  # 0.1% STT on sell
    total_cost_pct: float = None  # Calculated automatically
    
    # Slippage
    slippage_pct: float = 0.001  # 0.1% slippage
    
    def __post_init__(self):
        """Calculate total cost if not provided."""
        if self.total_cost_pct is None:
            # Buy costs: brokerage + transaction charges
            buy_cost = self.brokerage_pct + self.transaction_charges_pct
            # Sell costs: brokerage + transaction charges + STT
            sell_cost = self.brokerage_pct + self.transaction_charges_pct + self.stt_pct
            # Total cost per round trip
            self.total_cost_pct = buy_cost + sell_cost


@dataclass
class Trade:
    """Represents a single trade."""
    symbol: str
    entry_date: datetime
    entry_price: float
    quantity: int
    invested_amount: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_amount: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    holding_days: Optional[int] = None
    entry_signal: Optional[str] = None
    exit_signal: Optional[str] = None
    
    def close_trade(self, exit_date: datetime, exit_price: float, exit_signal: str = None):
        """Close the trade and calculate P&L."""
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_signal = exit_signal
        self.exit_amount = self.quantity * exit_price
        self.pnl = self.exit_amount - self.invested_amount
        self.pnl_pct = (self.pnl / self.invested_amount) * 100
        self.holding_days = (exit_date - self.entry_date).days
    
    def is_open(self) -> bool:
        """Check if trade is still open."""
        return self.exit_date is None


@dataclass
class PortfolioState:
    """Current state of the portfolio."""
    date: datetime
    cash: float
    positions: Dict[str, Trade] = field(default_factory=dict)
    closed_trades: List[Trade] = field(default_factory=list)
    trades_this_week: int = 0
    trades_this_month: int = 0
    week_start: datetime = None
    month_start: datetime = None
    
    def total_invested(self) -> float:
        """Total amount invested in open positions."""
        return sum(trade.invested_amount for trade in self.positions.values())
    
    def total_value(self) -> float:
        """Total portfolio value including cash."""
        position_value = sum(
            trade.quantity * trade.exit_price 
            if hasattr(trade, 'current_price') 
            else trade.invested_amount 
            for trade in self.positions.values()
        )
        return self.cash + position_value
    
    def available_cash(self, reserve_pct: float = 0.0) -> float:
        """Cash available for new positions (considering reserve)."""
        reserve = self.total_value() * reserve_pct
        return max(0, self.cash - reserve)
    
    def can_take_trade(self, config: PortfolioConfig) -> bool:
        """Check if new trade can be taken based on limits."""
        # Check position limit
        if len(self.positions) >= config.max_positions:
            return False
        
        # Check weekly limit
        if self.trades_this_week >= config.max_trades_per_week:
            return False
        
        # Check monthly limit
        if self.trades_this_month >= config.max_trades_per_month:
            return False
        
        return True


class PortfolioBacktester:
    """
    Backtest trading strategies with realistic portfolio management.
    
    Features:
    - Position sizing (fixed amount, equal weight, percentage)
    - Trade limits (per week, per month)
    - Maximum concurrent positions
    - Transaction costs and slippage
    - Cash management
    - Detailed trade tracking
    """
    
    def __init__(
        self, 
        strategy: BaseStrategy, 
        config: PortfolioConfig = None
    ):
        """
        Initialize portfolio backtester.
        
        Args:
            strategy: Trading strategy to backtest
            config: Portfolio configuration
        """
        self.strategy = strategy
        self.config = config or PortfolioConfig()
        self.portfolio_history: List[PortfolioState] = []
        self.current_portfolio: Optional[PortfolioState] = None
        
    def run(
        self, 
        data: Dict[str, pd.DataFrame] = None,
        symbols: List[str] = None,
        selection_type: str = None,
        selection_value: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        Run backtest on historical data.
        
        Args:
            data: Dictionary of {symbol: price_data_df}. If None, will load based on selection.
            symbols: List of symbols to backtest (alternative to data)
            selection_type: Stock selection type ('all', 'single', 'index', 'sector', 'custom')
            selection_value: Value for selection (index name, sector, etc.)
            start_date: Backtest start date
            end_date: Backtest end date
        
        Returns:
            Dictionary with backtest results
        """
        # Load data if not provided
        if data is None:
            from src.utils.stock_selector import StockSelector, load_stock_data
            
            selector = StockSelector()
            
            # Determine which stocks to load
            if symbols:
                selected_symbols = selector.get_by_custom_list(symbols)
            elif selection_type:
                selected_symbols = selector.get_by_criteria(selection_type, selection_value)
            else:
                logger.error("Must provide either 'data', 'symbols', or 'selection_type'")
                return {}
            
            if not selected_symbols:
                logger.error("No valid stocks selected")
                return {}
            
            # Filter by data availability
            selected_symbols = selector.filter_by_data_availability(selected_symbols, min_days=100)
            
            if not selected_symbols:
                logger.error("No stocks with sufficient data")
                return {}
            
            # Load data
            data = load_stock_data(selected_symbols)
        
        if not data:
            logger.error("No data available for backtesting")
            return {}
        
        logger.info(f"Starting portfolio backtest with {len(data)} symbols")
        logger.info(f"Initial capital: ₹{self.config.initial_capital:,.2f}")
        
        # Initialize portfolio
        self.current_portfolio = PortfolioState(
            date=start_date or min(df.index[0] for df in data.values()),
            cash=self.config.initial_capital,
            week_start=start_date,
            month_start=start_date
        )
        
        # Get all unique dates across all symbols
        all_dates = sorted(set(
            date for df in data.values() for date in df.index
            if (start_date is None or date >= start_date) and
               (end_date is None or date <= end_date)
        ))
        
        logger.info(f"Backtesting {len(all_dates)} trading days")
        
        # Run through each date
        for current_date in all_dates:
            self._process_day(current_date, data)
            
            # Store portfolio snapshot
            self.portfolio_history.append(self._snapshot_portfolio(current_date))
        
        # Close all remaining positions at end
        self._close_all_positions(all_dates[-1], data)
        
        # Calculate results
        results = self._calculate_results()
        
        logger.info(f"Backtest complete. Final value: ₹{results['final_value']:,.2f}")
        logger.info(f"Total return: {results['total_return_pct']:.2f}%")
        
        return results
    
    def _process_day(self, date: datetime, data: Dict[str, pd.DataFrame]):
        """Process a single trading day."""
        # Reset weekly counter if new week
        if self.current_portfolio.week_start is None or \
           (date - self.current_portfolio.week_start).days >= 7:
            self.current_portfolio.trades_this_week = 0
            self.current_portfolio.week_start = date
        
        # Reset monthly counter if new month
        if self.current_portfolio.month_start is None or \
           date.month != self.current_portfolio.month_start.month:
            self.current_portfolio.trades_this_month = 0
            self.current_portfolio.month_start = date
        
        # Check exit signals for open positions
        self._check_exits(date, data)
        
        # Check entry signals for new positions
        self._check_entries(date, data)
        
        # Update portfolio date
        self.current_portfolio.date = date
    
    def _check_exits(self, date: datetime, data: Dict[str, pd.DataFrame]):
        """Check and execute exit signals for open positions."""
        positions_to_close = []
        
        for symbol, trade in self.current_portfolio.positions.items():
            if symbol not in data:
                continue
            
            symbol_data = data[symbol]
            if date not in symbol_data.index:
                continue
            
            # Generate signals for this symbol
            signals = self.strategy.generate_signals(symbol_data[:date])
            
            # Get latest signal
            if signals and len(signals) > 0:
                latest_signal = signals[-1]
                
                # Check for exit signal
                if latest_signal.action == TradeAction.SELL:
                    positions_to_close.append((symbol, trade, latest_signal))
        
        # Execute exits
        for symbol, trade, signal in positions_to_close:
            self._execute_exit(symbol, trade, date, data, signal)
    
    def _check_entries(self, date: datetime, data: Dict[str, pd.DataFrame]):
        """Check and execute entry signals for new positions."""
        # Check if we can take new trades
        if not self.current_portfolio.can_take_trade(self.config):
            return
        
        # Collect all buy signals
        buy_signals = []
        
        for symbol, symbol_data in data.items():
            if date not in symbol_data.index:
                continue
            
            # Skip if already have position
            if symbol in self.current_portfolio.positions:
                continue
            
            # Generate signals
            signals = self.strategy.generate_signals(symbol_data[:date])
            
            if signals and len(signals) > 0:
                latest_signal = signals[-1]
                
                if latest_signal.action == TradeAction.BUY:
                    buy_signals.append((symbol, latest_signal, symbol_data))
        
        # Sort by signal strength (if available)
        if hasattr(buy_signals[0][1] if buy_signals else None, 'strength'):
            buy_signals.sort(key=lambda x: x[1].strength, reverse=True)
        
        # Execute entries (up to limits)
        for symbol, signal, symbol_data in buy_signals:
            if not self.current_portfolio.can_take_trade(self.config):
                break
            
            self._execute_entry(symbol, signal, date, symbol_data)
    
    def _execute_entry(
        self, 
        symbol: str, 
        signal: Signal, 
        date: datetime, 
        symbol_data: pd.DataFrame
    ):
        """Execute entry trade."""
        # Get entry price
        entry_price = symbol_data.loc[date, 'Close']
        entry_price_with_slippage = entry_price * (1 + self.config.slippage_pct)
        
        # Calculate position size
        position_amount = self._calculate_position_size()
        
        # Check if we have enough cash
        available = self.current_portfolio.available_cash(self.config.reserve_cash_pct)
        if position_amount > available:
            position_amount = available
        
        if position_amount < entry_price_with_slippage:
            return  # Not enough cash
        
        # Calculate quantity (whole shares only)
        quantity = int(position_amount / entry_price_with_slippage)
        if quantity == 0:
            return
        
        # Calculate actual invested amount including costs
        gross_amount = quantity * entry_price_with_slippage
        transaction_cost = gross_amount * (self.config.brokerage_pct + self.config.transaction_charges_pct)
        total_amount = gross_amount + transaction_cost
        
        # Create trade
        trade = Trade(
            symbol=symbol,
            entry_date=date,
            entry_price=entry_price_with_slippage,
            quantity=quantity,
            invested_amount=total_amount,
            entry_signal=signal.reason if hasattr(signal, 'reason') else 'BUY'
        )
        
        # Update portfolio
        self.current_portfolio.positions[symbol] = trade
        self.current_portfolio.cash -= total_amount
        self.current_portfolio.trades_this_week += 1
        self.current_portfolio.trades_this_month += 1
        
        logger.debug(f"BUY {symbol}: {quantity} @ ₹{entry_price_with_slippage:.2f} = ₹{total_amount:,.2f}")
    
    def _execute_exit(
        self, 
        symbol: str, 
        trade: Trade, 
        date: datetime, 
        data: Dict[str, pd.DataFrame],
        signal: Signal
    ):
        """Execute exit trade."""
        symbol_data = data[symbol]
        exit_price = symbol_data.loc[date, 'Close']
        exit_price_with_slippage = exit_price * (1 - self.config.slippage_pct)
        
        # Calculate exit amount
        gross_amount = trade.quantity * exit_price_with_slippage
        transaction_cost = gross_amount * (
            self.config.brokerage_pct + 
            self.config.transaction_charges_pct + 
            self.config.stt_pct
        )
        net_amount = gross_amount - transaction_cost
        
        # Close trade
        trade.close_trade(date, exit_price_with_slippage, signal.reason if hasattr(signal, 'reason') else 'SELL')
        trade.exit_amount = net_amount
        trade.pnl = net_amount - trade.invested_amount
        trade.pnl_pct = (trade.pnl / trade.invested_amount) * 100
        
        # Update portfolio
        self.current_portfolio.cash += net_amount
        del self.current_portfolio.positions[symbol]
        self.current_portfolio.closed_trades.append(trade)
        
        logger.debug(f"SELL {symbol}: {trade.quantity} @ ₹{exit_price_with_slippage:.2f} = ₹{net_amount:,.2f} (P&L: {trade.pnl_pct:.2f}%)")
    
    def _calculate_position_size(self) -> float:
        """Calculate position size based on configuration."""
        if self.config.position_size_method == PositionSizing.FIXED_AMOUNT:
            return self.config.position_size_value
        
        elif self.config.position_size_method == PositionSizing.EQUAL_WEIGHT:
            total_value = self.current_portfolio.total_value()
            return total_value / self.config.max_positions
        
        elif self.config.position_size_method == PositionSizing.PERCENTAGE:
            total_value = self.current_portfolio.total_value()
            return total_value * (self.config.position_size_value / 100)
        
        return self.config.position_size_value
    
    def _close_all_positions(self, date: datetime, data: Dict[str, pd.DataFrame]):
        """Close all remaining positions at end of backtest."""
        for symbol in list(self.current_portfolio.positions.keys()):
            trade = self.current_portfolio.positions[symbol]
            if symbol in data and date in data[symbol].index:
                # Create exit signal
                from src.strategy.base_strategy import Signal
                exit_signal = Signal(date=date, action=TradeAction.SELL, price=data[symbol].loc[date, 'Close'])
                self._execute_exit(symbol, trade, date, data, exit_signal)
    
    def _snapshot_portfolio(self, date: datetime) -> PortfolioState:
        """Create a snapshot of current portfolio state."""
        import copy
        return copy.deepcopy(self.current_portfolio)
    
    def _calculate_results(self) -> Dict:
        """Calculate comprehensive backtest results."""
        if not self.portfolio_history:
            return {}
        
        # Portfolio metrics
        initial_value = self.config.initial_capital
        final_value = self.current_portfolio.cash
        total_return = final_value - initial_value
        total_return_pct = (total_return / initial_value) * 100
        
        # Trade metrics
        all_trades = self.current_portfolio.closed_trades
        total_trades = len(all_trades)
        
        if total_trades > 0:
            winning_trades = [t for t in all_trades if t.pnl > 0]
            losing_trades = [t for t in all_trades if t.pnl < 0]
            
            win_rate = len(winning_trades) / total_trades * 100
            avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
            profit_factor = abs(sum(t.pnl for t in winning_trades) / sum(t.pnl for t in losing_trades)) if losing_trades and sum(t.pnl for t in losing_trades) != 0 else 0
            avg_holding_days = np.mean([t.holding_days for t in all_trades])
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0
            avg_holding_days = 0
        
        return {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades) if total_trades > 0 else 0,
            'losing_trades': len(losing_trades) if total_trades > 0 else 0,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'avg_holding_days': avg_holding_days,
            'max_positions': max(len(snapshot.positions) for snapshot in self.portfolio_history),
            'trades_history': all_trades,
            'portfolio_history': self.portfolio_history
        }
    
    def get_trades_df(self) -> pd.DataFrame:
        """Get all trades as DataFrame."""
        if not self.current_portfolio.closed_trades:
            return pd.DataFrame()
        
        trades_data = []
        for trade in self.current_portfolio.closed_trades:
            trades_data.append({
                'Symbol': trade.symbol,
                'Entry Date': trade.entry_date,
                'Entry Price': trade.entry_price,
                'Exit Date': trade.exit_date,
                'Exit Price': trade.exit_price,
                'Quantity': trade.quantity,
                'Invested': trade.invested_amount,
                'Exit Amount': trade.exit_amount,
                'P&L': trade.pnl,
                'P&L %': trade.pnl_pct,
                'Holding Days': trade.holding_days,
                'Entry Signal': trade.entry_signal,
                'Exit Signal': trade.exit_signal
            })
        
        return pd.DataFrame(trades_data)
