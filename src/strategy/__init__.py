"""
Strategy framework for backtesting and trading strategies.
"""
from src.strategy.base_strategy import BaseStrategy
from src.strategy.backtester import Backtester
from src.strategy.metrics import PerformanceMetrics

__all__ = ['BaseStrategy', 'Backtester', 'PerformanceMetrics']
