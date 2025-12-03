"""
Dataset analyzer for market-wide analysis across all stocks.
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from src.analysis.base_analyzer import BaseAnalyzer


class DatasetAnalyzer(BaseAnalyzer):
    """Analyzer for full dataset / market-wide analysis."""
    
    def __init__(self):
        """Initialize the dataset analyzer."""
        super().__init__()
    
    def analyze(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        top_n: int = 20,
        sample_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform market-wide analysis across all stocks.
        
        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            top_n: Number of top items to show in rankings
            sample_size: Optional limit on number of stocks to analyze (for performance)
            
        Returns:
            Dictionary containing market-wide analysis results
        """
        # Get all symbols
        all_symbols = self.get_all_symbols()
        
        if sample_size and sample_size < len(all_symbols):
            print(f"Sampling {sample_size} stocks from {len(all_symbols)} total stocks...")
            import random
            all_symbols = random.sample(all_symbols, sample_size)
        
        print(f"Analyzing {len(all_symbols)} stocks across the market...")
        
        # Load data for all stocks
        stock_data = {}
        for i, symbol in enumerate(all_symbols):
            if (i + 1) % 100 == 0:
                print(f"  Loaded {i + 1}/{len(all_symbols)} stocks...")
            
            df = self.load_stock_data(symbol)
            if df is not None:
                if start_date or end_date:
                    df = self.filter_by_date_range(df, start_date, end_date)
                if not df.empty:
                    stock_data[symbol] = df
        
        print(f"Successfully loaded data for {len(stock_data)} stocks.")
        
        if not stock_data:
            return {"error": "No data available for analysis"}
        
        # Perform analysis
        results = {
            "total_stocks_analyzed": len(stock_data),
            "total_stocks_in_metadata": len(all_symbols),
            "date_range": self._get_date_range(stock_data),
            "market_statistics": self._calculate_market_statistics(stock_data),
            "top_performers": self._get_top_performers(stock_data, top_n),
            "volume_analysis": self._analyze_market_volume(stock_data, top_n),
            "volatility_analysis": self._analyze_market_volatility(stock_data, top_n),
            "sector_analysis": self._analyze_by_sector(stock_data)
        }
        
        return results
    
    def _get_date_range(self, stock_data: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """Get the date range across all stocks."""
        all_dates = []
        for df in stock_data.values():
            if 'DATE' in df.columns:
                all_dates.extend(df['DATE'].tolist())
        
        if all_dates:
            return {
                "start": min(all_dates).strftime('%Y-%m-%d'),
                "end": max(all_dates).strftime('%Y-%m-%d')
            }
        return {"start": "N/A", "end": "N/A"}
    
    def _calculate_market_statistics(self, stock_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate overall market statistics."""
        all_returns = []
        all_volumes = []
        all_prices = []
        stocks_with_positive_return = 0
        stocks_with_negative_return = 0
        
        for symbol, df in stock_data.items():
            if 'CLOSE' in df.columns and len(df) >= 2:
                close_prices = df['CLOSE'].dropna()
                if len(close_prices) >= 2:
                    # Daily returns
                    daily_returns = close_prices.pct_change().dropna()
                    all_returns.extend(daily_returns.tolist())
                    all_prices.append(close_prices.iloc[-1])
                    
                    # Overall return
                    total_return = (close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0]
                    if total_return > 0:
                        stocks_with_positive_return += 1
                    elif total_return < 0:
                        stocks_with_negative_return += 1
            
            if 'VOLUME' in df.columns:
                volume = df['VOLUME'].dropna()
                all_volumes.extend(volume.tolist())
        
        stats = {
            "stocks_analyzed": len(stock_data),
            "advancing_stocks": stocks_with_positive_return,
            "declining_stocks": stocks_with_negative_return,
            "advance_decline_ratio": round(stocks_with_positive_return / stocks_with_negative_return, 2) if stocks_with_negative_return > 0 else float('inf')
        }
        
        if all_returns:
            returns_array = np.array(all_returns)
            stats["market_avg_daily_return"] = float(np.mean(returns_array) * 100)
            stats["market_return_std_dev"] = float(np.std(returns_array) * 100)
        
        if all_volumes:
            volumes_array = np.array(all_volumes)
            stats["market_avg_volume"] = float(np.mean(volumes_array))
            stats["market_total_volume"] = float(np.sum(volumes_array))
        
        if all_prices:
            stats["avg_stock_price"] = float(np.mean(all_prices))
            stats["median_stock_price"] = float(np.median(all_prices))
        
        return stats
    
    def _get_top_performers(self, stock_data: Dict[str, pd.DataFrame], top_n: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get top performing and worst performing stocks."""
        performance = []
        
        for symbol, df in stock_data.items():
            if 'CLOSE' not in df.columns or len(df) < 2:
                continue
            
            close_prices = df['CLOSE'].dropna()
            if len(close_prices) < 2:
                continue
            
            start_price = close_prices.iloc[0]
            end_price = close_prices.iloc[-1]
            total_return = ((end_price - start_price) / start_price) * 100
            
            info = self.get_stock_info(symbol)
            company_name = info.get("NAME OF COMPANY", symbol) if info else symbol
            
            performance.append({
                "symbol": symbol,
                "company": company_name,
                "return_pct": float(total_return),
                "start_price": float(start_price),
                "end_price": float(end_price)
            })
        
        performance.sort(key=lambda x: x['return_pct'], reverse=True)
        
        return {
            "top_gainers": performance[:top_n],
            "top_losers": performance[-top_n:][::-1]
        }
    
    def _analyze_market_volume(self, stock_data: Dict[str, pd.DataFrame], top_n: int) -> Dict[str, Any]:
        """Analyze volume across the market."""
        volume_data = []
        
        for symbol, df in stock_data.items():
            if 'VOLUME' not in df.columns:
                continue
            
            volume = df['VOLUME'].dropna()
            if len(volume) == 0:
                continue
            
            info = self.get_stock_info(symbol)
            company_name = info.get("NAME OF COMPANY", symbol) if info else symbol
            
            volume_data.append({
                "symbol": symbol,
                "company": company_name,
                "avg_volume": float(volume.mean()),
                "total_volume": float(volume.sum()),
                "max_volume": float(volume.max())
            })
        
        volume_data.sort(key=lambda x: x['avg_volume'], reverse=True)
        
        return {
            "top_volume_leaders": volume_data[:top_n]
        }
    
    def _analyze_market_volatility(self, stock_data: Dict[str, pd.DataFrame], top_n: int) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze volatility across the market."""
        volatility_data = []
        
        for symbol, df in stock_data.items():
            if 'CLOSE' not in df.columns or len(df) < 2:
                continue
            
            close_prices = df['CLOSE'].dropna()
            if len(close_prices) < 2:
                continue
            
            daily_returns = close_prices.pct_change().dropna()
            if len(daily_returns) == 0:
                continue
            
            volatility = daily_returns.std() * 100
            
            info = self.get_stock_info(symbol)
            company_name = info.get("NAME OF COMPANY", symbol) if info else symbol
            
            volatility_data.append({
                "symbol": symbol,
                "company": company_name,
                "volatility_pct": float(volatility)
            })
        
        volatility_data.sort(key=lambda x: x['volatility_pct'], reverse=True)
        
        return {
            "most_volatile": volatility_data[:top_n],
            "least_volatile": volatility_data[-top_n:][::-1]
        }
    
    def _analyze_by_sector(self, stock_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze performance by sector/index."""
        # Group by indices
        index_performance = {}
        
        for symbol in stock_data.keys():
            info = self.get_stock_info(symbol)
            if not info or 'INDICES' not in info:
                continue
            
            df = stock_data[symbol]
            if 'CLOSE' not in df.columns or len(df) < 2:
                continue
            
            close_prices = df['CLOSE'].dropna()
            if len(close_prices) < 2:
                continue
            
            total_return = ((close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0]) * 100
            
            for index_name in info['INDICES']:
                if index_name not in index_performance:
                    index_performance[index_name] = {
                        "returns": [],
                        "count": 0
                    }
                index_performance[index_name]["returns"].append(total_return)
                index_performance[index_name]["count"] += 1
        
        # Calculate average return per index
        index_summary = []
        for index_name, data in index_performance.items():
            if data["count"] > 0:
                avg_return = np.mean(data["returns"])
                index_summary.append({
                    "index": index_name,
                    "avg_return": float(avg_return),
                    "stock_count": data["count"]
                })
        
        # Sort by average return
        index_summary.sort(key=lambda x: x['avg_return'], reverse=True)
        
        return {
            "top_performing_indices": index_summary[:10],
            "worst_performing_indices": index_summary[-10:][::-1]
        }
    
    def print_analysis(self, results: Dict[str, Any]) -> None:
        """Print market analysis results in a formatted way."""
        if "error" in results:
            print(f"Error: {results['error']}")
            return
        
        print(f"\n{'='*80}")
        print("MARKET-WIDE ANALYSIS")
        print(f"{'='*80}")
        print(f"Total Stocks Analyzed: {results['total_stocks_analyzed']}")
        print(f"Date Range: {results['date_range']['start']} to {results['date_range']['end']}")
        
        # Market Statistics
        print(f"\n{'-'*80}")
        print("MARKET STATISTICS")
        print(f"{'-'*80}")
        stats = results['market_statistics']
        print(f"Advancing Stocks:     {stats['advancing_stocks']}")
        print(f"Declining Stocks:     {stats['declining_stocks']}")
        print(f"Advance/Decline Ratio: {stats['advance_decline_ratio']:.2f}")
        if 'market_avg_daily_return' in stats:
            print(f"Avg Daily Return:     {stats['market_avg_daily_return']:+.2f}%")
            print(f"Return Std Dev:       {stats['market_return_std_dev']:.2f}%")
        if 'avg_stock_price' in stats:
            print(f"Avg Stock Price:      ₹{stats['avg_stock_price']:.2f}")
        
        # Top Gainers
        print(f"\n{'-'*80}")
        print("TOP MARKET GAINERS")
        print(f"{'-'*80}")
        print(f"{'Symbol':<15} {'Company':<40} {'Return %':>10}")
        print(f"{'-'*80}")
        for stock in results['top_performers']['top_gainers']:
            company = stock['company'][:38] if len(stock['company']) > 38 else stock['company']
            print(f"{stock['symbol']:<15} {company:<40} {stock['return_pct']:>9.2f}%")
        
        # Top Losers
        print(f"\n{'-'*80}")
        print("TOP MARKET LOSERS")
        print(f"{'-'*80}")
        print(f"{'Symbol':<15} {'Company':<40} {'Return %':>10}")
        print(f"{'-'*80}")
        for stock in results['top_performers']['top_losers']:
            company = stock['company'][:38] if len(stock['company']) > 38 else stock['company']
            print(f"{stock['symbol']:<15} {company:<40} {stock['return_pct']:>9.2f}%")
        
        # Volume Leaders
        print(f"\n{'-'*80}")
        print("MARKET VOLUME LEADERS")
        print(f"{'-'*80}")
        print(f"{'Symbol':<15} {'Company':<40} {'Avg Volume':>15}")
        print(f"{'-'*80}")
        for stock in results['volume_analysis']['top_volume_leaders']:
            company = stock['company'][:38] if len(stock['company']) > 38 else stock['company']
            print(f"{stock['symbol']:<15} {company:<40} {stock['avg_volume']:>15,.0f}")
        
        # Top Performing Indices
        if results['sector_analysis']['top_performing_indices']:
            print(f"\n{'-'*80}")
            print("TOP PERFORMING INDICES")
            print(f"{'-'*80}")
            print(f"{'Index':<50} {'Avg Return %':>12} {'Stocks':>8}")
            print(f"{'-'*80}")
            for idx in results['sector_analysis']['top_performing_indices']:
                index_name = idx['index'][:48] if len(idx['index']) > 48 else idx['index']
                print(f"{index_name:<50} {idx['avg_return']:>11.2f}% {idx['stock_count']:>8}")
        
        print(f"\n{'='*80}\n")
