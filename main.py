import argparse
from src.data_fetch.fetch_eq_data import NSEDataFetcher

def main():
    parser = argparse.ArgumentParser(description="MKT Data Fetcher")
    parser.add_argument("--fetch-all", type=str, help="Fetch full history for a symbol")
    parser.add_argument("--fetch-latest", type=str, help="Fetch latest data for a symbol")
    parser.add_argument("--fetch-today", type=str, help="Fetch today's data for a symbol")
    parser.add_argument("--tag", type=str, help="Fetch by tag (requires TAG in metadata)")
    
    args = parser.parse_args()
    
    fetcher = NSEDataFetcher()
    
    if args.fetch_all:
        fetcher.fetch_all(args.fetch_all)
    elif args.fetch_latest:
        fetcher.fetch_latest(args.fetch_latest)
    elif args.fetch_today:
        fetcher.fetch_today(args.fetch_today)
    elif args.tag:
        fetcher.fetch_by_tag(args.tag, latest=True)
    else:
        print("No action specified. Use --help for options.")
        # Example usage if no args provided, or just print help
        # parser.print_help()

if __name__ == "__main__":
    main()
