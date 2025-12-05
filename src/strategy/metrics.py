"""
Performance metrics calculation for backtesting.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.utils.logger import get_logger
from src.config import settings

logger = get_logger(__name__)


class PerformanceMetrics:
    """Calculate performance metrics for trading strategies."""
    
    def __init__(self, risk_free_rate: float = None):
        """
        Initialize performance metrics calculator.
        
        Args:
            risk_free_rate: Annual risk-free rate (default from settings)
        """
        self.risk_free_rate = risk_free_rate or settings.RISK_FREE_RATE
        self.logger = get_logger(__name__)
    
    def calculate_all_metrics(
        self,
        equity_curve: pd.Series,
        trades: List[Dict[str, Any]],
        initial_capital: float
    ) -> Dict[str, Any]:
        """
        Calculate all performance metrics.
        
        Args:
            equity_curve: Series of portfolio values indexed by date
            trades: List of trade dictionaries
            initial_capital: Starting capital
        
        Returns:
            Dictionary of all metrics
        """
        metrics = {
            # Returns
            'total_return': self.total_return(equity_curve, initial_capital),
            'annual_return': self.annual_return(equity_curve, initial_capital),
            'monthly_return': self.monthly_return(equity_curve, initial_capital),
            
            # Risk-adjusted returns
            'sharpe_ratio': self.sharpe_ratio(equity_curve),
            'sortino_ratio': self.sortino_ratio(equity_curve),
            'calmar_ratio': self.calmar_ratio(equity_curve, initial_capital),
            
            # Drawdown metrics
            'max_drawdown': self.max_drawdown(equity_curve),
            'max_drawdown_duration': self.max_drawdown_duration(equity_curve),
            'avg_drawdown': self.avg_drawdown(equity_curve),
            
            # Trade statistics
            'total_trades': len(trades),
            'win_rate': self.win_rate(trades),
            'profit_factor': self.profit_factor(trades),
            'avg_trade_return': self.avg_trade_return(trades),
            'avg_win': self.avg_win(trades),
            'avg_loss': self.avg_loss(trades),
            'largest_win': self.largest_win(trades),
            'largest_loss': self.largest_loss(trades),
            
            # Exposure
            'market_exposure': self.market_exposure(trades, equity_curve),
        }
        
        return metrics
    
    def total_return(self, equity_curve: pd.Series, initial_capital: float) -> float:
        """Calculate total return percentage."""
        if len(equity_curve) == 0:
            return 0.0
        final_value = equity_curve.iloc[-1]
        return (final_value - initial_capital) / initial_capital
    
    def annual_return(self, equity_curve: pd.Series, initial_capital: float) -> float:
        """Calculate annualized return (CAGR)."""
        if len(equity_curve) < 2:
            return 0.0
        
        total_ret = self.total_return(equity_curve, initial_capital)
        
        # Calculate years
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        years = days / 365.25
        
        if years <= 0:
            return 0.0
        
        # CAGR = (Final/Initial)^(1/years) - 1
        return (1 + total_ret) ** (1 / years) - 1
    
    def monthly_return(self, equity_curve: pd.Series, initial_capital: float) -> float:
        """Calculate average monthly return."""
        annual = self.annual_return(equity_curve, initial_capital)
        return (1 + annual) ** (1/12) - 1
    
    def sharpe_ratio(self, equity_curve: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            equity_curve: Portfolio values
            periods_per_year: Trading periods per year (252 for daily)
        
        Returns:
            Sharpe ratio
        """
        if len(equity_curve) < 2:
            return 0.0
        
        # Calculate returns
        returns = equity_curve.pct_change().dropna()
        
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        # Excess returns
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        
        # Annualized Sharpe
        sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(periods_per_year)
        
        return sharpe
    
    def sortino_ratio(self, equity_curve: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate Sortino ratio (uses downside deviation).
        
        Args:
            equity_curve: Portfolio values
            periods_per_year: Trading periods per year
        
        Returns:
            Sortino ratio
        """
        if len(equity_curve) < 2:
            return 0.0
        
        returns = equity_curve.pct_change().dropna()
        
        if len(returns) == 0:
            return 0.0
        
        # Downside returns only
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        downside_std = downside_returns.std()
        
        sortino = (excess_returns.mean() / downside_std) * np.sqrt(periods_per_year)
        
        return sortino
    
    def max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown.
        
        Args:
            equity_curve: Portfolio values
        
        Returns:
            Maximum drawdown as a decimal (e.g., -0.20 for -20%)
        """
        if len(equity_curve) == 0:
            return 0.0
        
        # Calculate running maximum
        running_max = equity_curve.expanding().max()
        
        # Calculate drawdown
        drawdown = (equity_curve - running_max) / running_max
        
        return drawdown.min()
    
    def max_drawdown_duration(self, equity_curve: pd.Series) -> int:
        """
        Calculate maximum drawdown duration in days.
        
        Args:
            equity_curve: Portfolio values
        
        Returns:
            Maximum drawdown duration in days
        """
        if len(equity_curve) == 0:
            return 0
        
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        
        # Find periods in drawdown
        in_drawdown = drawdown < 0
        
        if not in_drawdown.any():
            return 0
        
        # Calculate duration of each drawdown period
        max_duration = 0
        current_duration = 0
        
        for is_dd in in_drawdown:
            if is_dd:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        return max_duration
    
    def avg_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate average drawdown."""
        if len(equity_curve) == 0:
            return 0.0
        
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        
        # Only negative drawdowns
        negative_dd = drawdown[drawdown < 0]
        
        return negative_dd.mean() if len(negative_dd) > 0 else 0.0
    
    def calmar_ratio(self, equity_curve: pd.Series, initial_capital: float) -> float:
        """
        Calculate Calmar ratio (Annual return / Max drawdown).
        
        Args:
            equity_curve: Portfolio values
            initial_capital: Starting capital
        
        Returns:
            Calmar ratio
        """
        annual_ret = self.annual_return(equity_curve, initial_capital)
        max_dd = abs(self.max_drawdown(equity_curve))
        
        if max_dd == 0:
            return 0.0
        
        return annual_ret / max_dd
    
    def win_rate(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate win rate."""
        if not trades:
            return 0.0
        
        wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        return wins / len(trades)
    
    def profit_factor(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        if not trades:
            return 0.0
        
        gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    def avg_trade_return(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate average trade return."""
        if not trades:
            return 0.0
        
        returns = [t.get('return', 0) for t in trades]
        return sum(returns) / len(returns)
    
    def avg_win(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate average winning trade."""
        wins = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]
        return sum(wins) / len(wins) if wins else 0.0
    
    def avg_loss(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate average losing trade."""
        losses = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0]
        return sum(losses) / len(losses) if losses else 0.0
    
    def largest_win(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate largest winning trade."""
        wins = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]
        return max(wins) if wins else 0.0
    
    def largest_loss(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate largest losing trade."""
        losses = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0]
        return min(losses) if losses else 0.0
    
    def market_exposure(
        self,
        trades: List[Dict[str, Any]],
        equity_curve: pd.Series
    ) -> float:
        """
        Calculate percentage of time in market.
        
        Args:
            trades: List of trades
            equity_curve: Portfolio values
        
        Returns:
            Market exposure as decimal (0-1)
        """
        if len(equity_curve) < 2:
            return 0.0
        
        total_days = (equity_curve.index[-1] - equity_curve.index[0]).days
        
        if total_days == 0:
            return 0.0
        
        # Calculate days in market (simplified - assumes one position at a time)
        days_in_market = 0
        for trade in trades:
            if 'entry_date' in trade and 'exit_date' in trade:
                duration = (trade['exit_date'] - trade['entry_date']).days
                days_in_market += duration
        
        return min(days_in_market / total_days, 1.0)
    
    def print_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Print performance metrics in a formatted way.
        
        Args:
            metrics: Dictionary of metrics
        """
        print("\n" + "="*60)
        print("PERFORMANCE METRICS")
        print("="*60)
        
        print("\n📊 Returns:")
        print(f"  Total Return:    {metrics.get('total_return', 0)*100:>8.2f}%")
        print(f"  Annual Return:   {metrics.get('annual_return', 0)*100:>8.2f}%")
        print(f"  Monthly Return:  {metrics.get('monthly_return', 0)*100:>8.2f}%")
        
        print("\n📈 Risk-Adjusted:")
        print(f"  Sharpe Ratio:    {metrics.get('sharpe_ratio', 0):>8.2f}")
        print(f"  Sortino Ratio:   {metrics.get('sortino_ratio', 0):>8.2f}")
        print(f"  Calmar Ratio:    {metrics.get('calmar_ratio', 0):>8.2f}")
        
        print("\n📉 Drawdown:")
        print(f"  Max Drawdown:    {metrics.get('max_drawdown', 0)*100:>8.2f}%")
        print(f"  Avg Drawdown:    {metrics.get('avg_drawdown', 0)*100:>8.2f}%")
        print(f"  Max DD Duration: {metrics.get('max_drawdown_duration', 0):>8} days")
        
        print("\n💼 Trade Statistics:")
        print(f"  Total Trades:    {metrics.get('total_trades', 0):>8}")
        print(f"  Win Rate:        {metrics.get('win_rate', 0)*100:>8.2f}%")
        print(f"  Profit Factor:   {metrics.get('profit_factor', 0):>8.2f}")
        print(f"  Avg Trade:       {metrics.get('avg_trade_return', 0)*100:>8.2f}%")
        print(f"  Avg Win:         {metrics.get('avg_win', 0):>8.2f}")
        print(f"  Avg Loss:        {metrics.get('avg_loss', 0):>8.2f}")
        print(f"  Largest Win:     {metrics.get('largest_win', 0):>8.2f}")
        print(f"  Largest Loss:    {metrics.get('largest_loss', 0):>8.2f}")
        
        print("\n⏱  Exposure:")
        print(f"  Market Exposure: {metrics.get('market_exposure', 0)*100:>8.2f}%")
        
        print("\n" + "="*60 + "\n")
