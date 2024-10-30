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
        
        if balance_sheet.empty:
            return None, None, None
        
        # Get market cap
        info = stock.info
        
        financial_data = {
            'Total_Debt': balance_sheet.loc['Total Debt'][0],
            'Goodwill': balance_sheet.loc['Goodwill'][0] if 'Goodwill' in balance_sheet.index else 0,
            'Intangible_Assets': balance_sheet.loc['Intangible Assets'][0] if 'Intangible Assets' in balance_sheet.index else 0,
            'Market_Value': info.get('marketCap', 0)
        }
        
        return hist, financial_data, info
        
    except Exception as e:
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
