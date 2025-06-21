import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from utils.calculations import calculate_debt_ratio, format_currency


class TestCalculations:
    """Test suite for calculation utilities"""
    
    def test_calculate_debt_ratio_normal(self):
        """Test debt ratio calculation with normal values"""
        financial_data = {
            'Long_Term_Debt': 1000000,
            'Total_Assets': 5000000,
            'Goodwill_And_Intangibles': 500000
        }
        
        result = calculate_debt_ratio(financial_data)
        expected = (1000000 / (5000000 - 500000)) * 100
        
        assert result == pytest.approx(expected, rel=1e-2)
    
    def test_calculate_debt_ratio_zero_debt(self):
        """Test debt ratio when debt is zero"""
        financial_data = {
            'Long_Term_Debt': 0,
            'Total_Assets': 5000000,
            'Goodwill_And_Intangibles': 500000
        }
        
        result = calculate_debt_ratio(financial_data)
        assert result == 0.0
    
    def test_calculate_debt_ratio_zero_adjusted_assets(self):
        """Test debt ratio when adjusted assets are zero"""
        financial_data = {
            'Long_Term_Debt': 1000000,
            'Total_Assets': 500000,
            'Goodwill_And_Intangibles': 500000
        }
        
        result = calculate_debt_ratio(financial_data)
        assert result is None
    
    def test_calculate_debt_ratio_missing_data(self):
        """Test debt ratio with missing data"""
        financial_data = {
            'Long_Term_Debt': 1000000,
            'Total_Assets': None,
            'Goodwill_And_Intangibles': 500000
        }
        
        result = calculate_debt_ratio(financial_data)
        assert result is None
    
    def test_format_currency_positive(self):
        """Test currency formatting with positive values"""
        assert format_currency(1234567) == "$1.23M"
        assert format_currency(1000) == "$1,000"
        assert format_currency(0) == "$0"
    
    def test_format_currency_negative(self):
        """Test currency formatting with negative values"""
        assert format_currency(-1234567) == "$-1.23M"
    
    def test_format_currency_none(self):
        """Test currency formatting with None"""
        assert format_currency(None) == "N/A"
    
    def test_format_currency_string(self):
        """Test currency formatting with string input"""
        assert format_currency("1234567") == "$1.23M"
    
    def test_format_currency_billions(self):
        """Test currency formatting with billion values"""
        assert format_currency(1234567890) == "$1.23B"
    
    def test_format_currency_small_values(self):
        """Test currency formatting with small values"""
        assert format_currency(12345) == "$12,345"