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
        
        # Get long term debt
        long_term_debt = 0
        if 'LongTermDebt' in balance_sheet.index:
            long_term_debt = balance_sheet.iloc[balance_sheet.index == 'LongTermDebt', 0].values[0]
        
        # Get total assets
        total_assets = 0
        if 'TotalAssets' in balance_sheet.index:
            total_assets = balance_sheet.iloc[balance_sheet.index == 'TotalAssets', 0].values[0]
        
        # Get goodwill and intangibles (combined)
        goodwill_and_intangibles = 0
        if 'GoodwillAndOtherIntangibleAssets' in balance_sheet.index:
            goodwill_and_intangibles = balance_sheet.iloc[balance_sheet.index == 'GoodwillAndOtherIntangibleAssets', 0].values[0]
        
        financial_data = {
            'Long_Term_Debt': long_term_debt,
            'Total_Assets': total_assets,
            'Goodwill_And_Intangibles': goodwill_and_intangibles,
            'Market_Value': info.get('marketCap', 0)
        }
        
        print("\nFinal financial data:")
        for key, value in financial_data.items():
            print(f"{key}: {value}")
        
        return hist, financial_data, info
        
    except Exception as e:
        print(f"Error in get_stock_data: {str(e)}")
        return None, None, None

def prepare_download_data(hist_data, financial_data, debt_ratio):
    """Prepare data for CSV download."""
    df = pd.DataFrame({
        'Date': hist_data.index,
        'Close': hist_data['Close'],
        'Long_Term_Debt': financial_data['Long_Term_Debt'],
        'Total_Assets': financial_data['Total_Assets'],
        'Goodwill_And_Intangibles': financial_data['Goodwill_And_Intangibles'],
        'Market_Value': financial_data['Market_Value'],
        'Debt_Ratio': debt_ratio
    })
    return df
