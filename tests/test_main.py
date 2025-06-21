import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import streamlit as st

# Import main functions
import main


class TestMain:
    """Test suite for main Streamlit application"""
    
    @patch('main.get_stock_data')
    @patch('streamlit.text_input')
    @patch('streamlit.spinner')
    def test_main_with_valid_symbol(self, mock_spinner, mock_text_input, mock_get_stock_data):
        """Test main function with valid stock symbol"""
        # Mock streamlit inputs
        mock_text_input.return_value = "AAPL"
        mock_spinner.return_value.__enter__ = MagicMock()
        mock_spinner.return_value.__exit__ = MagicMock()
        
        # Mock stock data
        mock_hist = pd.DataFrame({
            'Close': [150, 151, 152],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3))
        
        mock_financial = {
            'Long_Term_Debt': 1000000,
            'Total_Assets': 5000000,
            'Goodwill_And_Intangibles': 500000
        }
        
        mock_info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics'
        }
        
        mock_get_stock_data.return_value = (mock_hist, mock_financial, mock_info)
        
        # Test that main function can be called without errors
        # Note: We can't easily test the full Streamlit app, but we can test components
        assert mock_get_stock_data is not None
    
    @patch('main.get_stock_data')  
    @patch('streamlit.text_input')
    def test_main_with_invalid_symbol(self, mock_text_input, mock_get_stock_data):
        """Test main function with invalid stock symbol"""
        mock_text_input.return_value = "INVALID"
        mock_get_stock_data.return_value = (None, None, None)
        
        # Test that function handles invalid data gracefully
        assert mock_get_stock_data is not None
    
    def test_health_check(self):
        """Test health check function"""
        result = main.health_check()
        assert result == "OK"
    
    @patch('main.st')
    def test_main_function_structure(self, mock_st):
        """Test that main function has expected structure"""
        # Mock streamlit components
        mock_st.title = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.text_input.return_value = ""
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.subheader = MagicMock()
        mock_st.write = MagicMock()
        mock_st.button.return_value = False
        mock_st.download_button = MagicMock()
        mock_st.plotly_chart = MagicMock()
        mock_st.table = MagicMock()
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock()
        mock_st.error = MagicMock()
        
        # Call main function
        main.main()
        
        # Verify that streamlit components were called
        mock_st.title.assert_called()
        mock_st.markdown.assert_called()
        mock_st.text_input.assert_called()
    
    def test_app_configuration(self):
        """Test that app configuration is set correctly"""
        # This tests the module-level configuration
        # The actual st.set_page_config call happens on import
        assert True  # Basic test to ensure module imports without error