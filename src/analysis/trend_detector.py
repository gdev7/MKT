"""
Trend Detection for Stock Filtering

Identifies market trends:
- Uptrend (Bull Market): Higher highs and higher lows
- Downtrend (Bear Market): Lower highs and lower lows
- Sideways (Range-Bound): Horizontal movement within a range

Usage:
    from src.analysis.trend_detector import TrendDetector, TrendType
    
    detector = TrendDetector()
    trend = detector.detect_trend(df, period=20)
    
    # Filter stocks by trend
    if trend == TrendType.UPTREND:
        print("Stock is in uptrend")
"""

import pandas as pd
import numpy as np
from enum import Enum
from typing import Dict, Tuple, Optional
from pathlib import Path
from src.utils.data_reader import DataReader
from src.utils.data_reader import DataReader


class TrendType(Enum):
    """Trend classification types"""
    UPTREND = "uptrend"          # Bull market - higher highs, higher lows
    DOWNTREND = "downtrend"      # Bear market - lower highs, lower lows
    SIDEWAYS = "sideways"        # Range-bound - no clear direction
    UNKNOWN = "unknown"          # Insufficient data


class TrendDetector:
    """
    Detect market trends using swing highs and swing lows.
    
    Trend Detection Logic:
    - Uptrend: Last swing high > previous swing high AND last swing low > previous swing low
    - Downtrend: Last swing high < previous swing high AND last swing low < previous swing low
    - Sideways: Neither uptrend nor downtrend criteria met
    """
    
    def __init__(self, swing_period: int = 5):
        """
        Initialize trend detector.
        
        Args:
            swing_period: Number of periods to look for swing highs/lows (default: 5)
        """
        self.swing_period = swing_period
    
    def find_swing_highs(self, df: pd.DataFrame, period: int = 5) -> pd.Series:
        """
        Find swing highs (local maxima).
        
        A swing high occurs when the high at position i is greater than
        'period' highs before and after it.
        
        Args:
            df: DataFrame with 'high' column
            period: Lookback/forward period for comparison
            
        Returns:
            Series with True at swing high positions
        """
        highs = df['high'].values
        swing_highs = pd.Series(False, index=df.index)
        
        for i in range(period, len(highs) - period):
            is_swing_high = True
            
            # Check if current high is greater than 'period' highs before and after
            for j in range(1, period + 1):
                if highs[i] <= highs[i - j] or highs[i] <= highs[i + j]:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.iloc[i] = True
        
        return swing_highs
    
    def find_swing_lows(self, df: pd.DataFrame, period: int = 5) -> pd.Series:
        """
        Find swing lows (local minima).
        
        A swing low occurs when the low at position i is less than
        'period' lows before and after it.
        
        Args:
            df: DataFrame with 'low' column
            period: Lookback/forward period for comparison
            
        Returns:
            Series with True at swing low positions
        """
        lows = df['low'].values
        swing_lows = pd.Series(False, index=df.index)
        
        for i in range(period, len(lows) - period):
            is_swing_low = True
            
            # Check if current low is less than 'period' lows before and after
            for j in range(1, period + 1):
                if lows[i] >= lows[i - j] or lows[i] >= lows[i + j]:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.iloc[i] = True
        
        return swing_lows
    
    def detect_trend(self, df: pd.DataFrame, period: int = 20, 
                     min_swings: int = 2) -> TrendType:
        """
        Detect the current trend in price data.
        
        Args:
            df: DataFrame with OHLC data (must have 'high', 'low' columns)
            period: Lookback period for trend detection (default: 20 days)
            min_swings: Minimum number of swing points required (default: 2)
            
        Returns:
            TrendType: UPTREND, DOWNTREND, SIDEWAYS, or UNKNOWN
        """
        if len(df) < period:
            return TrendType.UNKNOWN
        
        # Get recent data
        recent_df = df.tail(period).copy()
        
        # Find swing points
        swing_highs = self.find_swing_highs(recent_df, self.swing_period)
        swing_lows = self.find_swing_lows(recent_df, self.swing_period)
        
        # Extract swing high and low values
        high_points = recent_df.loc[swing_highs, 'high'].values
        low_points = recent_df.loc[swing_lows, 'low'].values
        
        # Need at least min_swings points to determine trend
        if len(high_points) < min_swings or len(low_points) < min_swings:
            return TrendType.UNKNOWN
        
        # Compare last swing points with previous ones
        # Uptrend: Higher highs AND higher lows
        higher_highs = high_points[-1] > high_points[-2]
        higher_lows = low_points[-1] > low_points[-2]
        
        # Downtrend: Lower highs AND lower lows
        lower_highs = high_points[-1] < high_points[-2]
        lower_lows = low_points[-1] < low_points[-2]
        
        if higher_highs and higher_lows:
            return TrendType.UPTREND
        elif lower_highs and lower_lows:
            return TrendType.DOWNTREND
        else:
            return TrendType.SIDEWAYS
    
    def detect_trend_with_strength(self, df: pd.DataFrame, period: int = 20) -> Dict:
        """
        Detect trend with additional strength indicators.
        
        Args:
            df: DataFrame with OHLC data
            period: Lookback period
            
        Returns:
            Dict with trend type, strength score, and additional metrics
        """
        trend = self.detect_trend(df, period)
        
        # Calculate trend strength using linear regression slope
        recent_closes = df['close'].tail(period).values
        x = np.arange(len(recent_closes))
        
        # Fit linear regression
        coefficients = np.polyfit(x, recent_closes, 1)
        slope = coefficients[0]
        
        # Normalize slope as percentage of price
        avg_price = recent_closes.mean()
        slope_pct = (slope / avg_price) * 100 if avg_price > 0 else 0
        
        # Calculate R-squared for trend strength
        y_pred = np.polyval(coefficients, x)
        ss_res = np.sum((recent_closes - y_pred) ** 2)
        ss_tot = np.sum((recent_closes - recent_closes.mean()) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'trend': trend,
            'slope_pct': slope_pct,
            'r_squared': r_squared,
            'strength': 'strong' if r_squared > 0.7 else 'weak',
            'avg_price': avg_price,
            'current_price': recent_closes[-1],
            'price_change_pct': ((recent_closes[-1] - recent_closes[0]) / recent_closes[0] * 100)
        }
    
    def get_support_resistance(self, df: pd.DataFrame, period: int = 50) -> Tuple[float, float]:
        """
        Calculate support and resistance levels based on swing points.
        
        Args:
            df: DataFrame with OHLC data
            period: Lookback period
            
        Returns:
            Tuple of (support_level, resistance_level)
        """
        recent_df = df.tail(period).copy()
        
        swing_highs = self.find_swing_highs(recent_df, self.swing_period)
        swing_lows = self.find_swing_lows(recent_df, self.swing_period)
        
        # Resistance: Average of recent swing highs
        high_points = recent_df.loc[swing_highs, 'high'].values
        resistance = np.mean(high_points) if len(high_points) > 0 else recent_df['high'].max()
        
        # Support: Average of recent swing lows
        low_points = recent_df.loc[swing_lows, 'low'].values
        support = np.mean(low_points) if len(low_points) > 0 else recent_df['low'].min()
        
        return support, resistance


class TrendFilter:
    """
    Filter stocks based on trend criteria.
    
    Usage:
        trend_filter = TrendFilter()
        uptrend_stocks = trend_filter.filter_by_trend(
            symbols=['RELIANCE', 'TCS', 'INFY'],
            trend_type=TrendType.UPTREND
        )
    """
    
    def __init__(self, data_reader: Optional[DataReader] = None):
        """
        Initialize trend filter.
        
        Args:
            data_reader: DataReader instance (creates new one if None)
        """
        self.data_reader = data_reader or DataReader()
        self.detector = TrendDetector()
    
    def load_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Load stock data from CSV file.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            DataFrame with OHLC data or None if file not found
        """
        return self.data_reader.get_price_data(symbol)
    
    def filter_by_trend(self, symbols: list, trend_type: TrendType, 
                       period: int = 20, min_strength: float = 0.5) -> list:
        """
        Filter stocks by trend type.
        
        Args:
            symbols: List of stock symbols to filter
            trend_type: Desired trend type (UPTREND, DOWNTREND, or SIDEWAYS)
            period: Lookback period for trend detection
            min_strength: Minimum R-squared value for trend strength (0-1)
            
        Returns:
            List of dictionaries with stock symbol and trend details
        """
        filtered_stocks = []
        
        for symbol in symbols:
            df = self.load_stock_data(symbol)
            
            if df is None or len(df) < period:
                continue
            
            # Detect trend with strength
            trend_info = self.detector.detect_trend_with_strength(df, period)
            
            # Filter by trend type and strength
            if (trend_info['trend'] == trend_type and 
                trend_info['r_squared'] >= min_strength):
                
                support, resistance = self.detector.get_support_resistance(df, period)
                
                filtered_stocks.append({
                    'symbol': symbol,
                    'trend': trend_info['trend'].value,
                    'strength': trend_info['strength'],
                    'r_squared': round(trend_info['r_squared'], 3),
                    'slope_pct': round(trend_info['slope_pct'], 2),
                    'price_change_pct': round(trend_info['price_change_pct'], 2),
                    'current_price': round(trend_info['current_price'], 2),
                    'support': round(support, 2),
                    'resistance': round(resistance, 2)
                })
        
        # Sort by strength (R-squared)
        filtered_stocks.sort(key=lambda x: x['r_squared'], reverse=True)
        
        return filtered_stocks
    
    def get_all_trends(self, symbols: list, period: int = 20) -> pd.DataFrame:
        """
        Get trend classification for all symbols.
        
        Args:
            symbols: List of stock symbols
            period: Lookback period
            
        Returns:
            DataFrame with trend information for all stocks
        """
        results = []
        
        for symbol in symbols:
            df = self.load_stock_data(symbol)
            
            if df is None or len(df) < period:
                continue
            
            trend_info = self.detector.detect_trend_with_strength(df, period)
            support, resistance = self.detector.get_support_resistance(df, period)
            
            results.append({
                'symbol': symbol,
                'trend': trend_info['trend'].value,
                'strength': trend_info['strength'],
                'r_squared': round(trend_info['r_squared'], 3),
                'slope_pct': round(trend_info['slope_pct'], 2),
                'price_change_pct': round(trend_info['price_change_pct'], 2),
                'current_price': round(trend_info['current_price'], 2),
                'support': round(support, 2),
                'resistance': round(resistance, 2)
            })
        
        return pd.DataFrame(results)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        
        # Load data
        trend_filter = TrendFilter()
        df = trend_filter.load_stock_data(symbol)
        
        if df is not None:
            # Detect trend
            detector = TrendDetector()
            trend_info = detector.detect_trend_with_strength(df)
            support, resistance = detector.get_support_resistance(df)
            
            print(f"\n{'='*60}")
            print(f"TREND ANALYSIS: {symbol}")
            print(f"{'='*60}")
            print(f"Trend:          {trend_info['trend'].value.upper()}")
            print(f"Strength:       {trend_info['strength'].upper()}")
            print(f"R-Squared:      {trend_info['r_squared']:.3f}")
            print(f"Slope:          {trend_info['slope_pct']:.2f}%")
            print(f"Price Change:   {trend_info['price_change_pct']:.2f}%")
            print(f"Current Price:  ₹{trend_info['current_price']:.2f}")
            print(f"Support:        ₹{support:.2f}")
            print(f"Resistance:     ₹{resistance:.2f}")
            print(f"{'='*60}\n")
        else:
            print(f"Error: Could not load data for {symbol}")
    else:
        print("Usage: python trend_detector.py SYMBOL")
        print("Example: python trend_detector.py RELIANCE")
