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
        goodwill = 0
        intangibles = 0
        
        # Print all field values for debugging
        print("\nSearching for intangible-related fields...")
        for field in balance_sheet.index:
            if any(keyword in field.lower() for keyword in ['goodwill', 'intangible']):
                value = balance_sheet.iloc[balance_sheet.index == field, 0].values[0]
                print(f"Found field: {field} = {value}")
        
        # Check for combined field
        if 'GoodwillAndOtherIntangibleAssets' in balance_sheet.index:
            combined_value = balance_sheet.iloc[balance_sheet.index == 'GoodwillAndOtherIntangibleAssets', 0].values[0]
            print(f"\nFound combined GoodwillAndOtherIntangibleAssets: {combined_value}")
            
            # Set both goodwill and intangibles to half of the combined value
            # This reflects that we have a combined total but don't know the split
            goodwill = combined_value
            intangibles = 0  # We'll use the combined value as goodwill to avoid double counting
            
        else:
            # Look for separate fields
            if 'Goodwill' in balance_sheet.index:
                goodwill = balance_sheet.iloc[balance_sheet.index == 'Goodwill', 0].values[0]
                print(f"\nFound separate Goodwill: {goodwill}")
            
            intangible_fields = [
                'IntangibleAssets',
                'OtherIntangibleAssets',
                'NetIntangibleAssets',
                'IntangibleAssetsNet'
            ]
            
            # Find intangibles
            for field in intangible_fields:
                if field in balance_sheet.index:
                    intangibles = balance_sheet.iloc[balance_sheet.index == field, 0].values[0]
                    print(f"Found separate intangibles under field: {field} = {intangibles}")
                    break
        
        # Get total debt
        total_debt = 0
        if 'TotalDebt' in balance_sheet.index:
            total_debt = balance_sheet.iloc[balance_sheet.index == 'TotalDebt', 0].values[0]
        
        financial_data = {
            'Total_Debt': total_debt,
            'Goodwill': goodwill,
            'Intangible_Assets': intangibles,
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
        'Total_Debt': financial_data['Total_Debt'],
        'Market_Value': financial_data['Market_Value'],
        'Goodwill': financial_data['Goodwill'],
        'Intangible_Assets': financial_data['Intangible_Assets'],
        'Debt_Ratio': debt_ratio
    })
    return df
