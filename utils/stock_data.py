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
        print("\nAvailable Balance Sheet Fields:")
        print(balance_sheet.index.tolist())
        
        if balance_sheet.empty:
            return None, None, None
        
        # Get market cap
        info = stock.info
        
        # Initialize variables
        goodwill_and_intangibles = 0
        
        # Print all field values for debugging
        print("\nSearching for intangible-related fields...")
        for field in balance_sheet.index:
            if any(keyword in field.lower() for keyword in ['goodwill', 'intangible']):
                value = balance_sheet.iloc[balance_sheet.index == field, 0].values[0]
                print(f"Found field: {field} = {value}")
        
        # Get combined Goodwill and Intangible Assets value
        if 'Goodwill And Other Intangible Assets' in balance_sheet.index:
            goodwill_and_intangibles = balance_sheet.iloc[balance_sheet.index == 'Goodwill And Other Intangible Assets', 0].values[0]
            print(f"\nFound combined Goodwill And Other Intangible Assets: {goodwill_and_intangibles}")
        
        # Get long term debt
        long_term_debt = 0
        if 'Long Term Debt' in balance_sheet.index:
            long_term_debt = balance_sheet.iloc[balance_sheet.index == 'Long Term Debt', 0].values[0]
            print(f"\nFound long term debt: {long_term_debt}")
        
        financial_data = {
            'Long_Term_Debt': long_term_debt,
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
        'Market_Value': financial_data['Market_Value'],
        'Goodwill_And_Intangibles': financial_data['Goodwill_And_Intangibles'],
        'Debt_Ratio': debt_ratio
    })
    return df
