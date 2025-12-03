import argparse
from src.data_fetch.data_fetcher import DataFetcher
from src.data_fetch.metadata_sync import MetadataSync
from src.analysis.stock_analyzer import StockAnalyzer
from src.analysis.index_analyzer import IndexAnalyzer
from src.analysis.dataset_analyzer import DatasetAnalyzer

def main():
    parser = argparse.ArgumentParser(description="MKT Data Fetcher and Stock Analyzer")
    
    # Data fetching arguments
    parser.add_argument("--fetch-all", type=str, help="Fetch full history for a symbol")
    parser.add_argument("--fetch-latest", type=str, help="Fetch latest data for a symbol")
    parser.add_argument("--fetch-today", type=str, help="Fetch today's data for a symbol")
    parser.add_argument("--tag", type=str, help="Fetch by tag (requires TAG in metadata)")
    parser.add_argument("--sync-metadata", action="store_true", help="Sync metadata and raw data with NSE")
    
    # Analysis arguments
    parser.add_argument("--analyze-stock", type=str, help="Analyze a single stock by symbol")
    parser.add_argument("--analyze-index", type=str, help="Analyze stocks in a specific index (e.g., 'NIFTY 50')")
    parser.add_argument("--analyze-market", action="store_true", help="Analyze the entire market dataset")
    parser.add_argument("--list-indices", action="store_true", help="List all available indices")
    
    # Common analysis options
    parser.add_argument("--start-date", type=str, help="Start date for analysis (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date for analysis (YYYY-MM-DD)")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top items to show (default: 10)")
    parser.add_argument("--sample-size", type=int, help="Sample size for market analysis (for performance)")
    
    args = parser.parse_args()
    
    # Handle data fetching
    if args.sync_metadata:
        syncer = MetadataSync()
        syncer.sync_metadata()
    elif args.fetch_all or args.fetch_latest or args.fetch_today or args.tag:
        fetcher = DataFetcher()
        
        if args.fetch_all:
            fetcher.fetch_all(args.fetch_all)
        elif args.fetch_latest:
            fetcher.fetch_latest(args.fetch_latest)
        elif args.fetch_today:
            fetcher.fetch_today(args.fetch_today)
        elif args.tag:
            fetcher.fetch_by_tag(args.tag, latest=True)
    
    # Handle analysis
    elif args.analyze_stock:
        analyzer = StockAnalyzer()
        results = analyzer.analyze(
            symbol=args.analyze_stock,
            start_date=args.start_date,
            end_date=args.end_date
        )
        analyzer.print_analysis(results)
    
    elif args.analyze_index:
        analyzer = IndexAnalyzer()
        results = analyzer.analyze(
            index_name=args.analyze_index,
            start_date=args.start_date,
            end_date=args.end_date,
            top_n=args.top_n
        )
        analyzer.print_analysis(results)
    
    elif args.analyze_market:
        analyzer = DatasetAnalyzer()
        results = analyzer.analyze(
            start_date=args.start_date,
            end_date=args.end_date,
            top_n=args.top_n,
            sample_size=args.sample_size
        )
        analyzer.print_analysis(results)
    
    elif args.list_indices:
        analyzer = IndexAnalyzer()
        analyzer.list_available_indices()
    
    else:
        print("No action specified. Use --help for options.")

if __name__ == "__main__":
    main()

