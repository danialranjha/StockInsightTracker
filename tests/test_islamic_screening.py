from utils.islamic_screening import (calculate_islamic_ratios,
                                     calculate_ratios,
                                     check_business_practices)


class TestIslamicScreening:
    """Test suite for Islamic screening utilities"""

    def test_calculate_ratios_normal(self):
        """Test ratio calculations with normal values"""
        financial_data = {
            "Long_Term_Debt": 1000000,
            "Total_Assets": 5000000,
            "Goodwill_And_Intangibles": 0,
        }

        info = {
            "marketCap": 10000000000,
            "totalCash": 500000000,
            "shortTermInvestments": 0,
            "longTermInvestments": 0,
            "netReceivables": 800000000,
        }

        ratios = calculate_ratios(financial_data, info)

        assert ratios is not None
        assert "debt_ratio" in ratios
        assert "liquidity_ratio" in ratios
        assert "receivables_ratio" in ratios
        assert ratios["debt_ratio"] == 20.0  # (1M / 5M) * 100
        assert ratios["liquidity_ratio"] == 5.0  # (500M / 10B) * 100
        assert ratios["receivables_ratio"] == 8.0  # (800M / 10B) * 100

    def test_calculate_ratios_missing_data(self):
        """Test ratio calculations with missing data"""
        financial_data = {
            "Long_Term_Debt": None,
            "Total_Assets": 5000000,
            "Goodwill_And_Intangibles": 0,
        }

        info = {"marketCap": 10000000000}

        ratios = calculate_ratios(financial_data, info)

        assert ratios is not None
        assert ratios["receivables_ratio"] == 0.0  # Should default to 0

    def test_calculate_ratios_zero_market_cap(self):
        """Test ratio calculations with zero market cap"""
        financial_data = {
            "Long_Term_Debt": 1000000,
            "Total_Assets": 5000000,
            "Goodwill_And_Intangibles": 0,
        }

        info = {"marketCap": 0}

        ratios = calculate_ratios(financial_data, info)

        assert ratios is not None
        assert ratios["liquidity_ratio"] == 0.0
        assert ratios["receivables_ratio"] == 0.0

    def test_check_business_practices_compliant(self):
        """Test business practices check for compliant company"""
        info = {
            "longBusinessSummary": "Technology company that develops software",
            "sector": "Technology",
        }

        result = check_business_practices(info)

        assert result["is_business_compliant"] is True
        assert len(result["non_compliant_reasons"]) == 0

    def test_check_business_practices_financial_services(self):
        """Test business practices check for financial services"""
        info = {
            "longBusinessSummary": "Bank that provides financial services and lending",
            "sector": "Financial Services",
            "longName": "Big Bank Corp",
            "industry": "Commercial Banking",
        }

        result = check_business_practices(info)

        assert result["is_business_compliant"] is False
        assert len(result["non_compliant_reasons"]) > 0
        assert any(
            "financial services" in reason or "banking" in reason
            for reason in result["non_compliant_reasons"]
        )

    def test_check_business_practices_alcohol(self):
        """Test business practices check for alcohol-related business"""
        info = {
            "longBusinessSummary": "Company that produces alcoholic beverages",
            "sector": "Consumer Defensive",
        }

        result = check_business_practices(info)

        assert result["is_business_compliant"] is False
        assert len(result["non_compliant_reasons"]) > 0

    def test_calculate_islamic_ratios_compliant(self):
        """Test Islamic ratios calculation for compliant company"""
        financial_data = {
            "Long_Term_Debt": 500000,  # Low debt
            "Total_Assets": 5000000,
            "Goodwill_And_Intangibles": 0,
        }

        info = {
            "marketCap": 10000000000,  # 10B market cap
            "totalCash": 1000000000,  # Low liquidity ratio
            "shortTermInvestments": 0,
            "longTermInvestments": 0,
            "netReceivables": 1000000000,  # Low receivables ratio
            "longBusinessSummary": "Technology company",
            "sector": "Technology",
            "longName": "Tech Corp",
            "industry": "Software",
        }

        result = calculate_islamic_ratios(financial_data, info)

        assert result is not None
        assert result["is_fully_compliant"] is True
        assert result["is_debt_compliant"] is True
        assert result["is_liquidity_compliant"] is True
        assert result["is_receivables_compliant"] is True
        assert result["is_business_compliant"] is True
        assert len(result["non_compliant_reasons"]) == 0

    def test_calculate_islamic_ratios_non_compliant(self):
        """Test Islamic ratios calculation for non-compliant company"""
        financial_data = {
            "Long_Term_Debt": 2000000,  # High debt (40% of assets)
            "Total_Assets": 5000000,
            "Goodwill_And_Intangibles": 0,
        }

        info = {
            "marketCap": 10000000000,
            "totalCash": 4000000000,  # High liquidity (40% of market cap)
            "shortTermInvestments": 0,
            "longTermInvestments": 0,
            "netReceivables": 4000000000,  # High receivables (40% of market cap)
            "longBusinessSummary": "Banking and financial services",
            "sector": "Financial Services",
            "longName": "Big Bank Corp",
            "industry": "Commercial Banking",
        }

        result = calculate_islamic_ratios(financial_data, info)

        assert result is not None
        assert result["is_fully_compliant"] is False
        assert result["is_debt_compliant"] is False  # >33%
        assert result["is_liquidity_compliant"] is False  # >33%
        assert result["is_receivables_compliant"] is False  # >33%
        assert result["is_business_compliant"] is False
        assert len(result["non_compliant_reasons"]) > 0

    def test_calculate_islamic_ratios_missing_data(self):
        """Test Islamic ratios calculation with missing data"""
        financial_data = None
        info = None

        result = calculate_islamic_ratios(financial_data, info)

        assert result is None
