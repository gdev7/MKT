"""
Stock analyzer for analyzing individual stocks with technical indicators.
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from src.analysis.base_analyzer import BaseAnalyzer


class StockAnalyzer(BaseAnalyzer):
    """Analyzer for individual stock analysis with technical indicators."""
    
    def __init__(self):
        """Initialize the stock analyzer."""
        super().__init__()
    
    def analyze(
        self, 
        symbol: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        show_technicals: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a single stock.
        
        Args:
            symbol: Stock symbol to analyze
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            show_technicals: Whether to calculate technical indicators
            
        Returns:
            Dictionary containing analysis results
        """
        # Load stock data
        df = self.load_stock_data(symbol)
        if df is None:
            return {"error": f"Could not load data for {symbol}"}
        
        # Filter by date range if specified
        if start_date or end_date:
            df = self.filter_by_date_range(df, start_date, end_date)
        
        if df.empty:
            return {"error": "No data available for the specified date range"}
        
        # Get stock metadata
        stock_info = self.get_stock_info(symbol)
        
        # Perform analysis
        results = {
            "symbol": symbol,
            "company_name": stock_info.get("NAME OF COMPANY", "N/A") if stock_info else "N/A",
            "indices": stock_info.get("INDICES", []) if stock_info else [],
            "data_range": {
                "start": df['DATE'].min().strftime('%Y-%m-%d') if 'DATE' in df.columns else "N/A",
                "end": df['DATE'].max().strftime('%Y-%m-%d') if 'DATE' in df.columns else "N/A",
                "total_days": len(df)
            },
            "price_statistics": self._calculate_price_statistics(df),
            "volume_statistics": self._calculate_volume_statistics(df),
            "returns": self._calculate_returns(df)
        }
        
        if show_technicals:
            results["technical_indicators"] = self._calculate_technical_indicators(df)
        
        return results
    
    def _calculate_price_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate price-related statistics."""
        if 'CLOSE' not in df.columns:
            return {"error": "CLOSE column not found"}
        
        close_prices = df['CLOSE'].dropna()
        
        stats = {
            "current_price": float(close_prices.iloc[-1]) if len(close_prices) > 0 else None,
            "mean_price": float(close_prices.mean()),
            "median_price": float(close_prices.median()),
            "min_price": float(close_prices.min()),
            "max_price": float(close_prices.max()),
            "std_dev": float(close_prices.std()),
            "price_range": float(close_prices.max() - close_prices.min())
        }
        
        # Add high/low if available
        if 'HIGH' in df.columns and 'LOW' in df.columns:
            stats["52_week_high"] = float(df['HIGH'].tail(252).max()) if len(df) >= 252 else float(df['HIGH'].max())
            stats["52_week_low"] = float(df['LOW'].tail(252).min()) if len(df) >= 252 else float(df['LOW'].min())
        
        return stats
    
    def _calculate_volume_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volume-related statistics."""
        if 'VOLUME' not in df.columns:
            return {"error": "VOLUME column not found"}
        
        volume = df['VOLUME'].dropna()
        
        return {
            "avg_volume": float(volume.mean()),
            "median_volume": float(volume.median()),
            "max_volume": float(volume.max()),
            "min_volume": float(volume.min()),
            "current_volume": float(volume.iloc[-1]) if len(volume) > 0 else None
        }
    
    def _calculate_returns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate various return metrics."""
        if 'CLOSE' not in df.columns or len(df) < 2:
            return {"error": "Insufficient data for return calculation"}
        
        close_prices = df['CLOSE'].dropna()
        
        # Daily returns
        daily_returns = close_prices.pct_change().dropna()
        
        returns = {
            "daily_return_mean": float(daily_returns.mean()),
            "daily_return_std": float(daily_returns.std()),
            "daily_return_min": float(daily_returns.min()),
            "daily_return_max": float(daily_returns.max())
        }
        
        # Period returns
        if len(close_prices) > 0:
            current_price = close_prices.iloc[-1]
            
            # 1 week return
            if len(close_prices) >= 5:
                week_ago_price = close_prices.iloc[-5]
                returns["1_week_return"] = float((current_price - week_ago_price) / week_ago_price * 100)
            
            # 1 month return
            if len(close_prices) >= 21:
                month_ago_price = close_prices.iloc[-21]
                returns["1_month_return"] = float((current_price - month_ago_price) / month_ago_price * 100)
            
            # 3 month return
            if len(close_prices) >= 63:
                three_month_ago_price = close_prices.iloc[-63]
                returns["3_month_return"] = float((current_price - three_month_ago_price) / three_month_ago_price * 100)
            
            # YTD return
            if len(close_prices) >= 252:
                year_ago_price = close_prices.iloc[-252]
                returns["1_year_return"] = float((current_price - year_ago_price) / year_ago_price * 100)
        
        return returns
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators."""
        if 'CLOSE' not in df.columns:
            return {"error": "CLOSE column not found"}
        
        close_prices = df['CLOSE'].dropna()
        indicators = {}
        
        # Simple Moving Averages
        if len(close_prices) >= 20:
            indicators["SMA_20"] = float(close_prices.tail(20).mean())
        if len(close_prices) >= 50:
            indicators["SMA_50"] = float(close_prices.tail(50).mean())
        if len(close_prices) >= 200:
            indicators["SMA_200"] = float(close_prices.tail(200).mean())
        
        # Exponential Moving Averages
        if len(close_prices) >= 12:
            indicators["EMA_12"] = float(close_prices.ewm(span=12, adjust=False).mean().iloc[-1])
        if len(close_prices) >= 26:
            indicators["EMA_26"] = float(close_prices.ewm(span=26, adjust=False).mean().iloc[-1])
        
        # RSI (Relative Strength Index)
        if len(close_prices) >= 14:
            rsi = self._calculate_rsi(close_prices, period=14)
            if rsi is not None:
                indicators["RSI_14"] = float(rsi)
        
        # MACD
        if len(close_prices) >= 26:
            macd_data = self._calculate_macd(close_prices)
            if macd_data:
                indicators.update(macd_data)
        
        # Bollinger Bands
        if len(close_prices) >= 20:
            bb_data = self._calculate_bollinger_bands(close_prices, period=20)
            if bb_data:
                indicators.update(bb_data)
        
        return indicators
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return None
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None
    
    def _calculate_macd(self, prices: pd.Series) -> Optional[Dict[str, float]]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        if len(prices) < 26:
            return None
        
        ema_12 = prices.ewm(span=12, adjust=False).mean()
        ema_26 = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            "MACD_line": float(macd_line.iloc[-1]),
            "MACD_signal": float(signal_line.iloc[-1]),
            "MACD_histogram": float(histogram.iloc[-1])
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Optional[Dict[str, float]]:
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            return None
        
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            "BB_upper": float(upper_band.iloc[-1]),
            "BB_middle": float(sma.iloc[-1]),
            "BB_lower": float(lower_band.iloc[-1])
        }
    
    def print_analysis(self, results: Dict[str, Any]) -> None:
        """Print analysis results in a formatted way."""
        if "error" in results:
            print(f"Error: {results['error']}")
            return
        
        print(f"\n{'='*80}")
        print(f"STOCK ANALYSIS: {results['symbol']}")
        print(f"{'='*80}")
        print(f"Company: {results['company_name']}")
        
        if results['indices']:
            print(f"Indices: {', '.join(results['indices'][:5])}")
            if len(results['indices']) > 5:
                print(f"         ... and {len(results['indices']) - 5} more")
        
        print(f"\nData Range: {results['data_range']['start']} to {results['data_range']['end']}")
        print(f"Total Trading Days: {results['data_range']['total_days']}")
        
        # Price Statistics
        print(f"\n{'-'*80}")
        print("PRICE STATISTICS")
        print(f"{'-'*80}")
        ps = results['price_statistics']
        if 'error' not in ps:
            print(f"Current Price:    ₹{ps.get('current_price', 'N/A'):.2f}")
            print(f"Mean Price:       ₹{ps['mean_price']:.2f}")
            print(f"Min/Max Price:    ₹{ps['min_price']:.2f} / ₹{ps['max_price']:.2f}")
            if '52_week_high' in ps:
                print(f"52-Week High/Low: ₹{ps['52_week_high']:.2f} / ₹{ps['52_week_low']:.2f}")
            print(f"Std Deviation:    ₹{ps['std_dev']:.2f}")
        
        # Volume Statistics
        print(f"\n{'-'*80}")
        print("VOLUME STATISTICS")
        print(f"{'-'*80}")
        vs = results['volume_statistics']
        if 'error' not in vs:
            print(f"Current Volume:   {vs.get('current_volume', 'N/A'):,.0f}")
            print(f"Average Volume:   {vs['avg_volume']:,.0f}")
            print(f"Min/Max Volume:   {vs['min_volume']:,.0f} / {vs['max_volume']:,.0f}")
        
        # Returns
        print(f"\n{'-'*80}")
        print("RETURNS")
        print(f"{'-'*80}")
        ret = results['returns']
        if 'error' not in ret:
            if '1_week_return' in ret:
                print(f"1 Week Return:    {ret['1_week_return']:+.2f}%")
            if '1_month_return' in ret:
                print(f"1 Month Return:   {ret['1_month_return']:+.2f}%")
            if '3_month_return' in ret:
                print(f"3 Month Return:   {ret['3_month_return']:+.2f}%")
            if '1_year_return' in ret:
                print(f"1 Year Return:    {ret['1_year_return']:+.2f}%")
        
        # Technical Indicators
        if 'technical_indicators' in results:
            print(f"\n{'-'*80}")
            print("TECHNICAL INDICATORS")
            print(f"{'-'*80}")
            ti = results['technical_indicators']
            if 'error' not in ti:
                if 'SMA_20' in ti:
                    print(f"SMA 20:           ₹{ti['SMA_20']:.2f}")
                if 'SMA_50' in ti:
                    print(f"SMA 50:           ₹{ti['SMA_50']:.2f}")
                if 'SMA_200' in ti:
                    print(f"SMA 200:          ₹{ti['SMA_200']:.2f}")
                if 'RSI_14' in ti:
                    rsi = ti['RSI_14']
                    rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
                    print(f"RSI (14):         {rsi:.2f} ({rsi_status})")
                if 'MACD_line' in ti:
                    print(f"MACD Line:        {ti['MACD_line']:.2f}")
                    print(f"MACD Signal:      {ti['MACD_signal']:.2f}")
                    print(f"MACD Histogram:   {ti['MACD_histogram']:.2f}")
                if 'BB_upper' in ti:
                    print(f"Bollinger Upper:  ₹{ti['BB_upper']:.2f}")
                    print(f"Bollinger Middle: ₹{ti['BB_middle']:.2f}")
                    print(f"Bollinger Lower:  ₹{ti['BB_lower']:.2f}")
        
        print(f"\n{'='*80}\n")
