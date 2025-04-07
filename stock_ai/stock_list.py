# stock_ai/stock_list.py

import pandas as pd
import requests
from io import StringIO

def get_nse_stock_list():
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            df = df[['SYMBOL', 'NAME OF COMPANY']]
            df['EXCHANGE'] = 'NSE'
            return df
        else:
            print("Failed to fetch NSE stock list.")
            return pd.DataFrame()
    except Exception as e:
        print("Error fetching NSE list:", e)
        return pd.DataFrame()

def get_bse_stock_list():
    try:
        url = "https://www.bseindia.com/corporates/List_Scrips.aspx"
        print("Note: BSE full list is difficult to auto-fetch reliably. Using sample static data for now.")
        return pd.DataFrame([
            {'SYMBOL': 'RELIANCE', 'NAME OF COMPANY': 'Reliance Industries Ltd.', 'EXCHANGE': 'BSE'},
            {'SYMBOL': 'TCS', 'NAME OF COMPANY': 'Tata Consultancy Services Ltd.', 'EXCHANGE': 'BSE'}
        ])
    except Exception as e:
        print("Error fetching BSE list:", e)
        return pd.DataFrame()

def get_all_stock_list():
    nse_df = get_nse_stock_list()
    bse_df = get_bse_stock_list()
    return pd.concat([nse_df, bse_df], ignore_index=True)

if __name__ == "__main__":
    df = get_all_stock_list()
    print(df.head(20))
