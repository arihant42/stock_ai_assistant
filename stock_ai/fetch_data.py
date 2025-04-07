import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_price(symbol):
    url = f"https://www.moneycontrol.com/india/stockpricequote/{symbol.lower()}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.select_one(".nsecp")  # NSE price tag class
        if price_tag:
            price = float(price_tag.text.replace(",", ""))
            return price
    except Exception as e:
        print(f"[❌] {symbol}: {e}")
    return None

def main():
    symbols_map = {
        "RELIANCE": "energy-oil-drilling/relianceindustries/RI",
        "TCS": "computers-software/tataconsultancyservices/TCS",
        "INFY": "computers-software/infosys/IT",
        "HDFCBANK": "banks-private-sector/hdfcbank/HDF01",
        "ITC": "cigarettes/itc/ITC",
        "SBIN": "banks-public-sector/statebankofindia/SBI"
    }

    results = []
    for name, url_part in symbols_map.items():
        print(f"📊 Fetching {name}...")
        price = get_price(url_part)
        if price:
            print(f"✅ {name}: ₹{price}")
            results.append({
                "Symbol": name,
                "Price": price,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            print(f"❌ {name}: Failed to fetch data.")

    if results:
        df = pd.DataFrame(results)
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/nse_scraped_data.csv", index=False)
        print("📁 Data saved to data/nse_scraped_data.csv")
    else:
        print("⚠️ No data saved.")

if __name__ == "__main__":
    main()
