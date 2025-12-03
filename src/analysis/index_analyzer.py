"""
Index analyzer for analyzing groups of stocks within a specific index.
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from src.analysis.base_analyzer import BaseAnalyzer


class IndexAnalyzer(BaseAnalyzer):
    """Analyzer for index/group-based stock analysis."""
    
    def __init__(self):
        """Initialize the index analyzer."""
        super().__init__()
    
    def analyze(
        self, 
        index_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Perform analysis on all stocks within a specific index.
        
        Args:
            index_name: Name of the index (e.g., "NIFTY 50")
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            top_n: Number of top performers to show
            
        Returns:
            Dictionary containing index analysis results
        """
        # Get stocks in the index
        stocks = self.get_stocks_by_index(index_name)
        
        if not stocks:
            return {"error": f"No stocks found for index: {index_name}"}
        
        print(f"Analyzing {len(stocks)} stocks in {index_name}...")
        
        # Load data for all stocks
        stock_data = {}
        for symbol in stocks:
            df = self.load_stock_data(symbol)
            if df is not None:
                if start_date or end_date:
                    df = self.filter_by_date_range(df, start_date, end_date)
                if not df.empty:
                    stock_data[symbol] = df
        
        if not stock_data:
            return {"error": "No data available for stocks in this index"}
        
        # Perform analysis
        results = {
            "index_name": index_name,
            "total_stocks": len(stocks),
            "stocks_with_data": len(stock_data),
            "date_range": self._get_date_range(stock_data),
            "performance": self._analyze_performance(stock_data, top_n),
            "volume_leaders": self._analyze_volume(stock_data, top_n),
            "volatility": self._analyze_volatility(stock_data, top_n),
            "statistics": self._calculate_index_statistics(stock_data)
        }
        
        return results
    
    def _get_date_range(self, stock_data: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """Get the common date range across all stocks."""
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
    
    def _analyze_performance(self, stock_data: Dict[str, pd.DataFrame], top_n: int) -> Dict[str, Any]:
        """Analyze performance of stocks in the index."""
        performance = []
        
        for symbol, df in stock_data.items():
            if 'CLOSE' not in df.columns or len(df) < 2:
                continue
            
            close_prices = df['CLOSE'].dropna()
            if len(close_prices) < 2:
                continue
            
            # Calculate returns
            start_price = close_prices.iloc[0]
            end_price = close_prices.iloc[-1]
            total_return = ((end_price - start_price) / start_price) * 100
            
            # Get company name
            info = self.get_stock_info(symbol)
            company_name = info.get("NAME OF COMPANY", symbol) if info else symbol
            
            performance.append({
                "symbol": symbol,
                "company": company_name,
                "start_price": float(start_price),
                "end_price": float(end_price),
                "return_pct": float(total_return)
            })
        
        # Sort by return
        performance.sort(key=lambda x: x['return_pct'], reverse=True)
        
        return {
            "top_gainers": performance[:top_n],
            "top_losers": performance[-top_n:][::-1],
            "all_stocks": performance
        }
    
    def _analyze_volume(self, stock_data: Dict[str, pd.DataFrame], top_n: int) -> List[Dict[str, Any]]:
        """Analyze volume leaders in the index."""
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
                "total_volume": float(volume.sum())
            })
        
        # Sort by average volume
        volume_data.sort(key=lambda x: x['avg_volume'], reverse=True)
        
        return volume_data[:top_n]
    
    def _analyze_volatility(self, stock_data: Dict[str, pd.DataFrame], top_n: int) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze volatility of stocks in the index."""
        volatility_data = []
        
        for symbol, df in stock_data.items():
            if 'CLOSE' not in df.columns or len(df) < 2:
                continue
            
            close_prices = df['CLOSE'].dropna()
            if len(close_prices) < 2:
                continue
            
            # Calculate daily returns
            daily_returns = close_prices.pct_change().dropna()
            
            if len(daily_returns) == 0:
                continue
            
            # Volatility is standard deviation of returns
            volatility = daily_returns.std() * 100  # Convert to percentage
            
            info = self.get_stock_info(symbol)
            company_name = info.get("NAME OF COMPANY", symbol) if info else symbol
            
            volatility_data.append({
                "symbol": symbol,
                "company": company_name,
                "volatility_pct": float(volatility),
                "avg_daily_return": float(daily_returns.mean() * 100)
            })
        
        # Sort by volatility
        volatility_data.sort(key=lambda x: x['volatility_pct'], reverse=True)
        
        return {
            "most_volatile": volatility_data[:top_n],
            "least_volatile": volatility_data[-top_n:][::-1]
        }
    
    def _calculate_index_statistics(self, stock_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate overall statistics for the index."""
        all_returns = []
        all_volumes = []
        current_prices = []
        
        for df in stock_data.values():
            if 'CLOSE' in df.columns and len(df) >= 2:
                close_prices = df['CLOSE'].dropna()
                if len(close_prices) >= 2:
                    daily_returns = close_prices.pct_change().dropna()
                    all_returns.extend(daily_returns.tolist())
                    current_prices.append(close_prices.iloc[-1])
            
            if 'VOLUME' in df.columns:
                volume = df['VOLUME'].dropna()
                all_volumes.extend(volume.tolist())
        
        stats = {}
        
        if all_returns:
            returns_array = np.array(all_returns)
            stats["avg_daily_return"] = float(np.mean(returns_array) * 100)
            stats["median_daily_return"] = float(np.median(returns_array) * 100)
            stats["return_std_dev"] = float(np.std(returns_array) * 100)
        
        if all_volumes:
            volumes_array = np.array(all_volumes)
            stats["avg_volume"] = float(np.mean(volumes_array))
            stats["total_volume"] = float(np.sum(volumes_array))
        
        if current_prices:
            stats["avg_current_price"] = float(np.mean(current_prices))
            stats["median_current_price"] = float(np.median(current_prices))
        
        return stats
    
    def print_analysis(self, results: Dict[str, Any]) -> None:
        """Print index analysis results in a formatted way."""
        if "error" in results:
            print(f"Error: {results['error']}")
            return
        
        print(f"\n{'='*80}")
        print(f"INDEX ANALYSIS: {results['index_name']}")
        print(f"{'='*80}")
        print(f"Total Stocks in Index: {results['total_stocks']}")
        print(f"Stocks with Data: {results['stocks_with_data']}")
        print(f"Date Range: {results['date_range']['start']} to {results['date_range']['end']}")
        
        # Index Statistics
        print(f"\n{'-'*80}")
        print("INDEX STATISTICS")
        print(f"{'-'*80}")
        stats = results['statistics']
        if 'avg_daily_return' in stats:
            print(f"Avg Daily Return:     {stats['avg_daily_return']:+.2f}%")
            print(f"Return Std Dev:       {stats['return_std_dev']:.2f}%")
        if 'avg_volume' in stats:
            print(f"Avg Volume:           {stats['avg_volume']:,.0f}")
        if 'avg_current_price' in stats:
            print(f"Avg Current Price:    ₹{stats['avg_current_price']:.2f}")
        
        # Top Gainers
        print(f"\n{'-'*80}")
        print("TOP GAINERS")
        print(f"{'-'*80}")
        print(f"{'Symbol':<15} {'Company':<40} {'Return %':>10}")
        print(f"{'-'*80}")
        for stock in results['performance']['top_gainers']:
            company = stock['company'][:38] if len(stock['company']) > 38 else stock['company']
            print(f"{stock['symbol']:<15} {company:<40} {stock['return_pct']:>9.2f}%")
        
        # Top Losers
        print(f"\n{'-'*80}")
        print("TOP LOSERS")
        print(f"{'-'*80}")
        print(f"{'Symbol':<15} {'Company':<40} {'Return %':>10}")
        print(f"{'-'*80}")
        for stock in results['performance']['top_losers']:
            company = stock['company'][:38] if len(stock['company']) > 38 else stock['company']
            print(f"{stock['symbol']:<15} {company:<40} {stock['return_pct']:>9.2f}%")
        
        # Volume Leaders
        print(f"\n{'-'*80}")
        print("VOLUME LEADERS")
        print(f"{'-'*80}")
        print(f"{'Symbol':<15} {'Company':<40} {'Avg Volume':>15}")
        print(f"{'-'*80}")
        for stock in results['volume_leaders']:
            company = stock['company'][:38] if len(stock['company']) > 38 else stock['company']
            print(f"{stock['symbol']:<15} {company:<40} {stock['avg_volume']:>15,.0f}")
        
        # Most Volatile
        print(f"\n{'-'*80}")
        print("MOST VOLATILE STOCKS")
        print(f"{'-'*80}")
        print(f"{'Symbol':<15} {'Company':<40} {'Volatility %':>12}")
        print(f"{'-'*80}")
        for stock in results['volatility']['most_volatile']:
            company = stock['company'][:38] if len(stock['company']) > 38 else stock['company']
            print(f"{stock['symbol']:<15} {company:<40} {stock['volatility_pct']:>11.2f}%")
        
        print(f"\n{'='*80}\n")
    
    def list_available_indices(self) -> None:
        """List all available indices."""
        indices = self.get_all_indices()
        
        print(f"\n{'='*80}")
        print("AVAILABLE INDICES")
        print(f"{'='*80}")
        print(f"Total Indices: {len(indices)}\n")
        
        for i, index_name in enumerate(indices, 1):
            stocks_count = len(self.get_stocks_by_index(index_name))
            print(f"{i:3d}. {index_name:<50} ({stocks_count} stocks)")
        
        print(f"\n{'='*80}\n")
