import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from utils.cache import rate_limit
import requests
import time

# --- Robust error handling and retry logic for yfinance requests ---
def retry_with_backoff(func, *args, **kwargs):
    """
    Retry a function up to 3 times with exponential backoff if HTTP 429 is encountered.
    """
    max_retries = 3
    delay = 2
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Check for HTTP 429 Too Many Requests
            if hasattr(e, "response") and getattr(e.response, "status_code", None) == 429:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise
            elif "429" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise
            else:
                raise

# --- Set custom User-Agent for all yfinance requests ---
# This ensures all yfinance HTTP requests use a custom User-Agent header
yf.shared._requests_kwargs = {"headers": {"User-Agent": "StockInsightTracker/1.0 (+https://yourdomain.com)"}}

@rate_limit()
def get_stock_data(symbol):
    """Fetch stock data and financial information with retry and rate limiting."""
    try:
        # Use retry logic for all yfinance data fetches to handle HTTP 429 errors
        stock = retry_with_backoff(yf.Ticker, symbol)
        
        # Get historical data with retry
        hist = retry_with_backoff(stock.history, period="1y")
        
        # Get balance sheet with retry
        balance_sheet = retry_with_backoff(lambda: stock.balance_sheet)
        
        # Debug logging
        print("\nAvailable Balance Sheet Fields:")
        print(balance_sheet.index.tolist())
        
        if balance_sheet.empty:
            return None, None, None
        
        # Get info with retry
        info = retry_with_backoff(lambda: stock.info)
        
        # Initialize variables
        goodwill_and_intangibles = 0
        
        # Print all field values for debugging
        print("\nSearching for intangible-related fields...")
        for field in balance_sheet.index:
            if any(keyword in field.lower() for keyword in ['goodwill', 'intangible']):
                value = balance_sheet.loc[field][0]
                print(f"Found field: {field} = {value}")
        
        # Get combined Goodwill and Intangible Assets value
        if 'Goodwill And Other Intangible Assets' in balance_sheet.index:
            goodwill_and_intangibles = balance_sheet.loc['Goodwill And Other Intangible Assets'][0]
            print(f"\nFound combined Goodwill And Other Intangible Assets: {goodwill_and_intangibles}")
        
        # Get long term debt
        long_term_debt = 0
        if 'Long Term Debt' in balance_sheet.index:
            long_term_debt = balance_sheet.loc['Long Term Debt'][0]
            print(f"\nFound long term debt: {long_term_debt}")
        
        # Get total assets
        total_assets = 0
        if 'Total Assets' in balance_sheet.index:
            total_assets = balance_sheet.loc['Total Assets'][0]
            print(f"\nFound total assets: {total_assets}")
        
        financial_data = {
            'Long_Term_Debt': long_term_debt,
            'Goodwill_And_Intangibles': goodwill_and_intangibles,
            'Total_Assets': total_assets
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
        'Debt_Ratio': debt_ratio
    })
    return df
