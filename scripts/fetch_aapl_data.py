import yfinance as yf
import json
from datetime import datetime

def fetch_and_save_data(symbols):
    """Fetch data for given symbols and save it for test mocking"""
    for symbol in symbols:
        # Fetch data
        stock = yf.Ticker(symbol)
        
        # Get historical data and convert to dict for JSON serialization
        hist = stock.history(period="1y")
        hist_dict = {
            "Date": [d.strftime("%Y-%m-%d") for d in hist.index],
            "Close": hist['Close'].tolist()
        }
        
        # Get balance sheet
        balance_sheet = stock.balance_sheet
        
        # Get financial data
        financial_data = {
            'Long_Term_Debt': float(balance_sheet.loc['Long Term Debt'][0]) if 'Long Term Debt' in balance_sheet.index else 0,
            'Goodwill_And_Intangibles': float(balance_sheet.loc['Goodwill And Other Intangible Assets'][0]) if 'Goodwill And Other Intangible Assets' in balance_sheet.index else 0,
            'Total_Assets': float(balance_sheet.loc['Total Assets'][0]) if 'Total Assets' in balance_sheet.index else 0
        }
        
        # Get info
        info = stock.info
        
        # Save data to files
        with open(f'tests/mock_data/{symbol.lower()}_hist_data.json', 'w') as f:
            json.dump(hist_dict, f, indent=2)
            
        with open(f'tests/mock_data/{symbol.lower()}_financial_data.json', 'w') as f:
            json.dump(financial_data, f, indent=2)
            
        with open(f'tests/mock_data/{symbol.lower()}_info.json', 'w') as f:
            json.dump(info, f, indent=2)
            
        print(f"{symbol} data has been saved to tests/mock_data/")

if __name__ == "__main__":
    symbols = ["AAPL", "AMZN", "BAC"]
    fetch_and_save_data(symbols)

if __name__ == "__main__":
    fetch_and_save_aapl_data()
