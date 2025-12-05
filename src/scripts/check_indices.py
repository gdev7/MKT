"""
Check INDICES field distribution in metadata.
"""
import json
from pathlib import Path

# Load metadata
metadata_file = Path("data/metadata/stocks_metadata.json")
with open(metadata_file, 'r') as f:
    data = json.load(f)

# Analyze INDICES field
total_stocks = len(data)
stocks_with_indices = {k: v for k, v in data.items() if 'INDICES' in v and v['INDICES']}
stocks_without_indices = {k: v for k, v in data.items() if 'INDICES' not in v or not v.get('INDICES')}

print("="*60)
print("INDICES FIELD ANALYSIS")
print("="*60)
print(f"Total stocks:              {total_stocks}")
print(f"Stocks WITH indices:       {len(stocks_with_indices)} ({len(stocks_with_indices)/total_stocks*100:.2f}%)")
print(f"Stocks WITHOUT indices:    {len(stocks_without_indices)} ({len(stocks_without_indices)/total_stocks*100:.2f}%)")

# Show distribution of index membership
if stocks_with_indices:
    index_counts = {}
    for symbol, info in stocks_with_indices.items():
        indices = info.get('INDICES', [])
        for idx in indices:
            index_counts[idx] = index_counts.get(idx, 0) + 1
    
    print(f"\nTotal unique indices: {len(index_counts)}")
    print("\nTop 20 indices by membership:")
    print("-"*60)
    for idx, count in sorted(index_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"{idx:45} {count:4} stocks")
    
    # Sample stocks with indices
    print(f"\nSample stocks WITH indices (first 10):")
    print("-"*60)
    for symbol in list(stocks_with_indices.keys())[:10]:
        indices = stocks_with_indices[symbol]['INDICES']
        print(f"{symbol:15} - {len(indices):2} indices: {', '.join(indices[:3])}{'...' if len(indices) > 3 else ''}")
    
    # Sample stocks without indices
    print(f"\nSample stocks WITHOUT indices (first 10):")
    print("-"*60)
    for symbol in list(stocks_without_indices.keys())[:10]:
        company_name = stocks_without_indices[symbol].get('NAME OF COMPANY', 'N/A')
        print(f"{symbol:15} - {company_name}")

print("="*60)
