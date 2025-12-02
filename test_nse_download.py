import requests
import pandas as pd
import io

url = "https://www.nseindia.com/api/equity-stockIndices?csv=true&index=NIFTY%20SMALLCAP%20100&selectValFormat=crores"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com/market-data/live-equity-market",
}

try:
    session = requests.Session()
    # Visit homepage first to get cookies
    session.get("https://www.nseindia.com", headers=headers)
    
    response = session.get(url, headers=headers)
    response.raise_for_status()
    
    print("Download successful")
    content = response.text
    print("First 500 characters:")
    print(content[:500])
    
    # Split by lines to see structure
    lines = content.splitlines()
    print(f"\nTotal lines: {len(lines)}")
    for i, line in enumerate(lines[:15]):
        print(f"Line {i}: {line}")

    # Try parsing with different options
    # Robust strategy: Find the start of data and prepend clean header
    data_start_marker = '"NIFTY SMALLCAP 100"'
    start_index = content.find(data_start_marker)
    
    if start_index != -1:
        print(f"\nFound data start at index {start_index}")
        raw_data = content[start_index:]
        
        # Define clean header (based on observation)
        clean_header = '"SYMBOL","OPEN","HIGH","LOW","PREV. CLOSE","LTP","INDICATIVE CLOSE","CHNG","%CHNG","VOLUME","VALUE","52W H","52W L","30 D %CHNG","365 D % CHNG"\n'
        
        final_csv = clean_header + raw_data
        
        try:
            print("\nTrying to parse with replaced header:")
            df = pd.read_csv(io.StringIO(final_csv))
            print(df.head())
            print(df.columns)
            
            if "SYMBOL" in df.columns:
                print("\nSymbols found:")
                print(df["SYMBOL"].head())
        except Exception as e:
            print(f"\nReplaced header parse failed: {e}")
    else:
        print("\nCould not find data start marker")
except Exception as e:
    print(f"Error: {e}")
