import pytest
from unittest.mock import patch, MagicMock
import json
import logging
import os

from utils.stock_data import get_stock_data
from utils.islamic_screening import calculate_islamic_ratios, calculate_ratios, check_business_practices

def load_mock_data(symbol):
    """Load mock data from JSON files for a given symbol"""
    base_path = "tests/mock_data"
    
    with open(os.path.join(base_path, f"{symbol.lower()}_hist_data.json")) as f:
        hist_data = json.load(f)
    
    with open(os.path.join(base_path, f"{symbol.lower()}_financial_data.json")) as f:
        financial_data = json.load(f)
    
    with open(os.path.join(base_path, f"{symbol.lower()}_info.json")) as f:
        info = json.load(f)
    
    # Use a smaller subset of historical data for efficiency
    hist_data["Date"] = hist_data["Date"][:30]  # Last 30 days
    hist_data["Close"] = hist_data["Close"][:30]
    
    return hist_data, financial_data, info

def run_islamic_compliance_test(symbol, expected_compliance, expected_reasons):
    """Test Islamic compliance calculation using real mock data"""
    mock_hist_data, mock_financial_data, mock_info = load_mock_data(symbol)

    # Mock yfinance
    import sys
    sys.modules['yfinance'] = MagicMock()

    with patch("test_main.get_stock_data", return_value=(mock_hist_data, mock_financial_data, mock_info)):
        hist_data, financial_data, info = get_stock_data(symbol)
        
        # Verify mock data is loaded correctly
        assert hist_data is not None, f"Mock historical data not loaded for {symbol}"
        assert financial_data is not None, f"Mock financial data not loaded for {symbol}"
        assert info is not None, f"Mock company info not loaded for {symbol}"
        
        islamic_ratios = calculate_islamic_ratios(financial_data, info)
        
        # Verify Islamic screening results
        assert islamic_ratios is not None, f"Islamic ratios calculation failed for {symbol}"
        assert islamic_ratios["is_fully_compliant"] == expected_compliance, \
            f"Expected compliance for {symbol}: {expected_compliance}, but got: {islamic_ratios['is_fully_compliant']}"
        assert islamic_ratios["non_compliant_reasons"] == expected_reasons, \
            f"Expected reasons for {symbol}: {expected_reasons}, but got: {islamic_ratios['non_compliant_reasons']}"

def test_calculate_ratios():
    symbol = "AAPL"
    mock_hist_data, mock_financial_data, mock_info = load_mock_data(symbol)
    
    ratios = calculate_ratios(mock_financial_data, mock_info)
    
    assert ratios is not None, "calculate_ratios returned None"
    assert ratios['debt_ratio'] is not None, "Debt ratio is None"
    assert ratios['liquidity_ratio'] is not None, "Liquidity ratio is None"
    assert ratios['receivables_ratio'] is not None, "Receivables ratio is None"

def test_check_business_practices():
    symbol = "AAPL"
    mock_hist_data, mock_financial_data, mock_info = load_mock_data(symbol)
    
    business_practices = check_business_practices(mock_info)
    
    assert business_practices is not None, "check_business_practices returned None"
    assert 'is_business_compliant' in business_practices, "is_business_compliant not in result"
    assert 'non_compliant_reasons' in business_practices, "non_compliant_reasons not in result"

def test_aapl_business_practices_compliance(caplog):
    """Test AAPL business practices compliance - should be compliant after credit card keyword fix
    
    AAPL was previously marked non-compliant due to 'Apple Card, a co-branded credit card'
    in its business description. After fixing the keywords to be more specific
    ('credit card company/issuer/provider'), AAPL should now be correctly marked as compliant
    since it's a technology company that partners with financial institutions rather than
    being a credit card issuer itself.
    """
    with caplog.at_level(logging.DEBUG):
        run_islamic_compliance_test(
            symbol="AAPL",
            expected_compliance=True,
            expected_reasons=[]
        )
    # Print captured logs
    for record in caplog.records:
        print(record.message)

def test_amzn_compliance():
    """Test AMZN compliance"""
    run_islamic_compliance_test(
        symbol="AMZN",
        expected_compliance=True,
        expected_reasons=[]
    )

def test_bac_compliance():
    """Test BAC compliance"""
    run_islamic_compliance_test(
        symbol="BAC",
        expected_compliance=False,
        expected_reasons=[
            "Company's business description indicates involvement in financial services",
            "Company operates in interest-based financial services"
        ]
    )
