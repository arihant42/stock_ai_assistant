import pandas as pd
import requests
import os
from io import StringIO
from datetime import datetime

def fetch_nse_stock_list(save_to='data/nse/nse_stock_list.csv'):
    url = "https://www1.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www1.nseindia.com/"
    }

    try:
        session = requests.Session()
        session.headers.update(headers)
        session.get("https://www1.nseindia.com", timeout=10)

        response = session.get(url, timeout=10)
        response.encoding = 'utf-8'

        # Save raw content for debug if needed
        os.makedirs('data/nse/raw', exist_ok=True)
        with open('data/nse/raw/equity_l_raw.csv', 'w', encoding='utf-8') as raw:
            raw.write(response.text)

        # Read using fallback logic
        try:
            df = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
        except Exception as e:
            print(f"[❌] Pandas fallback failed: {e}")
            return []

        if 'SYMBOL' not in df.columns or 'NAME OF COMPANY' not in df.columns:
            print(f"[❌] Required columns not found. Available columns: {df.columns.tolist()}")
            return []

        df = df[['SYMBOL', 'NAME OF COMPANY']].dropna()
        df.drop_duplicates(subset='SYMBOL', inplace=True)

        os.makedirs(os.path.dirname(save_to), exist_ok=True)
        df.to_csv(save_to, index=False)
        print(f"✅ NSE stock list saved to {save_to}")
        return df['SYMBOL'].tolist()

    except Exception as e:
        print(f"[❌] NSE fetch failed: {e}")
        return []

def fetch_bse_stock_list(save_to='data/bse/bse_stock_list.csv'):
    url = "https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE_{}{}.zip"
    today = datetime.now()
    day = today.strftime('%d')
    month = today.strftime('%m')
    year = today.strftime('%y')

    full_url = url.format(day, month + year)
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(full_url, headers=headers)
        zip_path = 'data/bse/stock_list.zip'

        with open(zip_path, 'wb') as f:
            f.write(r.content)

        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('data/bse/')

        for file in os.listdir('data/bse/'):
            if file.endswith('.csv'):
                df = pd.read_csv(f'data/bse/{file}')
                df = df[['SC_CODE', 'SC_NAME']].dropna()
                df.to_csv(save_to, index=False)
                print(f"✅ BSE stock list saved to {save_to}")
                return df['SC_CODE'].tolist()

        print("[❌] No CSV found in BSE ZIP")
        return []

    except Exception as e:
        print(f"[❌] BSE fetch failed: {e}")
        return []

if __name__ == "__main__":
    print("📥 Fetching NSE Stock List...")
    nse_symbols = fetch_nse_stock_list()
    print(f"✅ Total NSE Stocks: {len(nse_symbols)}")

    print("\n📥 Fetching BSE Stock List...")
    bse_symbols = fetch_bse_stock_list()
    print(f"✅ Total BSE Stocks: {len(bse_symbols)}")
