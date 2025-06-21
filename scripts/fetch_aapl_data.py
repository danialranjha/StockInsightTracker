import json
import time

import requests
import requests_cache
import yfinance as yf

# Enable HTTP response caching for all requests (including yfinance) for 1 hour
# to reduce duplicate API calls and avoid 429 errors
requests_cache.install_cache("yfinance_cache", expire_after=3600)

# Set a custom User-Agent for all requests (including yfinance)
requests.utils.default_headers()[
    "User-Agent"
] = "StockInsightTracker/1.0 (+https://yourdomain.com)"


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
            if (
                hasattr(e, "response")
                and getattr(e.response, "status_code", None) == 429
            ):
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
yf.shared._requests_kwargs = {
    "headers": {"User-Agent": "StockInsightTracker/1.0 (+https://yourdomain.com)"}
}


def fetch_and_save_data(symbols):
    """Fetch data for given symbols and save it for test mocking.

    Uses caching, rate limiting, and retry logic.
    """
    for symbol in symbols:
        # Rate limiting: wait at least 5 seconds between requests per symbol
        # to avoid 429 errors
        time.sleep(5)

        # Fetch data with retry logic for all yfinance calls
        stock = retry_with_backoff(yf.Ticker, symbol)

        # Get historical data and convert to dict for JSON serialization
        hist = retry_with_backoff(stock.history, period="1y")
        hist_dict = {
            "Date": [d.strftime("%Y-%m-%d") for d in hist.index],
            "Close": hist["Close"].tolist(),
        }

        # Get balance sheet
        balance_sheet = retry_with_backoff(lambda: stock.balance_sheet)

        # Get financial data
        financial_data = {
            "Long_Term_Debt": (
                float(balance_sheet.loc["Long Term Debt"][0])
                if "Long Term Debt" in balance_sheet.index
                else 0
            ),
            "Goodwill_And_Intangibles": (
                float(balance_sheet.loc["Goodwill And Other Intangible Assets"][0])
                if "Goodwill And Other Intangible Assets" in balance_sheet.index
                else 0
            ),
            "Total_Assets": (
                float(balance_sheet.loc["Total Assets"][0])
                if "Total Assets" in balance_sheet.index
                else 0
            ),
        }

        # Get info
        info = retry_with_backoff(lambda: stock.info)

        # Save data to files
        with open(f"tests/mock_data/{symbol.lower()}_hist_data.json", "w") as f:
            json.dump(hist_dict, f, indent=2)

        with open(f"tests/mock_data/{symbol.lower()}_financial_data.json", "w") as f:
            json.dump(financial_data, f, indent=2)

        with open(f"tests/mock_data/{symbol.lower()}_info.json", "w") as f:
            json.dump(info, f, indent=2)

        print(f"{symbol} data has been saved to tests/mock_data/")


if __name__ == "__main__":
    symbols = ["AAPL", "AMZN", "BAC"]
    fetch_and_save_data(symbols)
