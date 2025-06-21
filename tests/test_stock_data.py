from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from utils.stock_data import get_stock_data, prepare_download_data, retry_with_backoff


class TestStockData:
    """Test suite for stock data utilities"""

    @patch("utils.stock_data.yf.Ticker")
    @patch("utils.stock_data.retry_with_backoff")
    def test_get_stock_data_success(self, mock_retry, mock_ticker):
        """Test successful stock data retrieval"""
        # Mock data
        mock_hist = pd.DataFrame(
            {"Close": [100, 101, 102], "Volume": [1000, 1100, 1200]}
        )

        # Create balance sheet with proper index
        mock_balance_sheet = pd.DataFrame(
            data=[[500000], [2000000], [100000]],
            index=[
                "Long Term Debt",
                "Total Assets",
                "Goodwill And Other Intangible Assets",
            ],
            columns=[0],
        )

        mock_info = {
            "longName": "Test Company",
            "sector": "Technology",
            "longBusinessSummary": "A test company",
        }

        # Setup mocks with proper call order
        mock_stock_instance = MagicMock()
        mock_retry.side_effect = [
            mock_stock_instance,  # yf.Ticker call
            mock_hist,  # stock.history call
            mock_balance_sheet,  # stock.balance_sheet call
            mock_info,  # stock.info call
        ]

        result = get_stock_data("TEST")

        assert result is not None
        hist_data, financial_data, info = result

        # Verify results
        assert hist_data is not None
        assert financial_data is not None
        assert info is not None
        assert financial_data["Long_Term_Debt"] == 500000

    def test_retry_with_backoff_success(self):
        """Test retry logic with successful function"""

        def successful_function():
            return "success"

        result = retry_with_backoff(successful_function)
        assert result == "success"

    @patch("time.sleep")
    def test_retry_with_backoff_http_429(self, mock_sleep):
        """Test retry logic with HTTP 429 error"""
        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # Create a mock exception with 429 status
                error = requests.exceptions.HTTPError()
                error.response = MagicMock()
                error.response.status_code = 429
                raise error
            return "success after retries"

        result = retry_with_backoff(failing_function)
        assert result == "success after retries"
        assert call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep twice before success

    @patch("time.sleep")
    def test_retry_with_backoff_429_in_message(self, mock_sleep):
        """Test retry logic with 429 in error message"""
        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("HTTP 429 Too Many Requests")
            return "success"

        result = retry_with_backoff(failing_function)
        assert result == "success"
        assert call_count == 2
        assert mock_sleep.call_count == 1

    def test_retry_with_backoff_other_error(self):
        """Test retry logic with non-429 error"""

        def failing_function():
            raise ValueError("Different error")

        with pytest.raises(ValueError, match="Different error"):
            retry_with_backoff(failing_function)

    def test_prepare_download_data(self):
        """Test download data preparation"""
        hist_data = pd.DataFrame(
            {
                "Close": [100, 101, 102],
                "Open": [99, 100, 101],
                "High": [101, 102, 103],
                "Low": [98, 99, 100],
                "Volume": [1000, 1100, 1200],
            }
        )

        financial_data = {
            "Long_Term_Debt": 500000,
            "Total_Assets": 2000000,
            "Goodwill_And_Intangibles": 100000,
        }

        debt_ratio = 25.0

        result = prepare_download_data(hist_data, financial_data, debt_ratio)

        assert isinstance(result, pd.DataFrame)
        assert "Debt_Ratio" in result.columns
        assert result["Debt_Ratio"].iloc[0] == debt_ratio

    @patch("utils.stock_data.yf.Ticker")
    @patch("utils.stock_data.retry_with_backoff")
    def test_get_stock_data_failure(self, mock_retry, mock_ticker):
        """Test stock data retrieval failure"""
        mock_retry.side_effect = Exception("API Error")

        result = get_stock_data("INVALID")

        # Should return None values on error
        assert result == (None, None, None)
