import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(symbol):
    """Fetch stock data and financial information."""
    try:
        stock = yf.Ticker(symbol)
        
        # Get historical data
        hist = stock.history(period="1y")
        
        # Get balance sheet
        balance_sheet = stock.balance_sheet
        
        # Debug logging
        print("Available Balance Sheet Fields:")
        print(balance_sheet.index.tolist())
        print("\nBalance Sheet Data Sample:")
        print(balance_sheet)
        
        if balance_sheet.empty:
            return None, None, None
        
        # Get market cap
        info = stock.info
        
        # Try different possible field names for goodwill and intangibles
        goodwill = 0
        intangibles = 0
        
        goodwill_fields = ['Goodwill', 'GoodwillAndOtherIntangibleAssets', 'GoodWill']
        intangible_fields = ['Intangible Assets', 'IntangibleAssets', 'OtherIntangibleAssets']
        
        for field in goodwill_fields:
            if field in balance_sheet.index:
                goodwill = balance_sheet.iloc[balance_sheet.index == field, 0].values[0]
                print(f"Found goodwill under field: {field}")
                break
                
        for field in intangible_fields:
            if field in balance_sheet.index:
                intangibles = balance_sheet.iloc[balance_sheet.index == field, 0].values[0]
                print(f"Found intangibles under field: {field}")
                break
        
        financial_data = {
            'Total_Debt': balance_sheet.iloc[balance_sheet.index == 'Total Debt', 0].values[0] if 'Total Debt' in balance_sheet.index else balance_sheet.iloc[balance_sheet.index == 'TotalDebt', 0].values[0],
            'Goodwill': goodwill,
            'Intangible_Assets': intangibles,
            'Market_Value': info.get('marketCap', 0)
        }
        
        return hist, financial_data, info
        
    except Exception as e:
        print(f"Error in get_stock_data: {str(e)}")
        return None, None, None

def prepare_download_data(hist_data, financial_data, debt_ratio):
    """Prepare data for CSV download."""
    df = pd.DataFrame({
        'Date': hist_data.index,
        'Close': hist_data['Close'],
        'Total_Debt': financial_data['Total_Debt'],
        'Market_Value': financial_data['Market_Value'],
        'Goodwill': financial_data['Goodwill'],
        'Intangible_Assets': financial_data['Intangible_Assets'],
        'Debt_Ratio': debt_ratio
    })
    return df
