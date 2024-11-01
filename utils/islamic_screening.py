from utils.calculations import calculate_debt_ratio

def calculate_islamic_ratios(financial_data, info):
    """Calculate Islamic compliance ratios."""
    try:
        market_cap = info.get('marketCap', 0)
        if market_cap == 0:
            return None

        # Use the same debt ratio calculation as in calculations.py
        debt_ratio = calculate_debt_ratio(financial_data)
        if debt_ratio is None:
            return None

        # Get financial metrics
        cash_and_investments = sum([
            info.get('totalCash', 0),
            info.get('shortTermInvestments', 0),
            info.get('longTermInvestments', 0)
        ])
        accounts_receivable = info.get('netReceivables', 0)

        # Calculate other ratios using market cap
        liquidity_ratio = (cash_and_investments / market_cap) * 100
        receivables_ratio = (accounts_receivable / market_cap) * 100

        # Check compliance
        is_debt_compliant = debt_ratio < 33
        is_liquidity_compliant = liquidity_ratio < 33
        is_receivables_compliant = receivables_ratio < 33

        # Get business activity info
        sector = info.get('sector', '').lower()
        industry = info.get('industry', '').lower()
        company_name = info.get('longName', '').lower()

        # Enhanced list of non-compliant business activities
        non_compliant_keywords = [
            'alcohol', 'brewery', 'distillery', 'gambling', 'casino',
            'tobacco', 'pork', 'weapons', 'defense', 'entertainment',
            'hotel', 'banking', 'insurance', 'interest', 'investment bank',
            'financial services', 'mortgage', 'credit services',
            'investment management', 'capital markets'
        ]

        # Specific checks for financial sector
        is_financial_sector = sector == 'financial services' or 'financial' in sector
        is_bank = any(word in company_name or word in industry for word in ['bank', 'banking'])
        
        # Combined business compliance check
        is_business_compliant = not (
            any(keyword in sector or keyword in industry 
                for keyword in non_compliant_keywords) or
            is_financial_sector or
            is_bank
        )

        return {
            'debt_ratio': round(debt_ratio, 2),
            'liquidity_ratio': round(liquidity_ratio, 2),
            'receivables_ratio': round(receivables_ratio, 2),
            'is_debt_compliant': is_debt_compliant,
            'is_liquidity_compliant': is_liquidity_compliant,
            'is_receivables_compliant': is_receivables_compliant,
            'is_business_compliant': is_business_compliant,
            'sector': sector,
            'industry': industry,
            'is_fully_compliant': (
                is_debt_compliant and 
                is_liquidity_compliant and 
                is_receivables_compliant and 
                is_business_compliant
            )
        }
    except Exception as e:
        print(f"Error in Islamic screening calculations: {str(e)}")
        return None
