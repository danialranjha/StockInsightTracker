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
        business_summary = info.get('longBusinessSummary', '').lower()

        # Enhanced list of non-compliant business activities with categories
        non_compliant_categories = {
            'alcohol': [
                'alcohol', 'brewery', 'breweries', 'distillery', 'distilleries', 
                'wine', 'spirits', 'beer', 'liquor', 'beverages-alcoholic',
                'craft brew', 'craft beer', 'wines & spirits', 'winery',
                'brewing', 'alcoholic beverages', 'malt beverages',
                'beverage-brewers', 'beverage distribution-alcohol'
            ],
            'gambling': ['gambling', 'casino', 'betting', 'wagering', 'lottery'],
            'tobacco': ['tobacco', 'cigarettes', 'cigars', 'smoking products', 'vaping'],
            'prohibited food': ['pork', 'swine', 'ham', 'bacon'],
            'weapons': ['weapons', 'defense', 'ammunition', 'firearms', 'missiles'],
            'adult entertainment': [
                'adult entertainment', 'adult content', 'gambling', 'casino',
                'nightclub', 'cabaret'
            ],
            'financial services': [
                'commercial bank', 'investment bank', 'mortgage', 'credit services',
                'credit card', 'lending services', 'consumer lending',
                'asset management', 'capital markets', 'insurance',
                'investment brokerage', 'wealth management', 'retail banking',
                'corporate banking', 'financial exchange'
            ]
        }

        # Check each category and collect non-compliant reasons
        non_compliant_reasons = []
        
        for category, keywords in non_compliant_categories.items():
            # Check in sector, industry, company name and business summary
            if any(keyword in text for keyword in keywords for text in [sector, industry, company_name]):
                non_compliant_reasons.append(f"Company operates in {category} sector")

        # Specific checks for financial institutions
        financial_indicators = [
            'bank', 'banking', 'credit union', 'savings and loan',
            'mortgage reit', 'financial exchange', 'insurance carrier',
            'investment brokerage', 'asset management', 'wealth management'
        ]

        # More precise financial sector identification
        is_financial_institution = (
            any(indicator in industry.lower() for indicator in financial_indicators) or
            any(indicator in company_name.lower() for indicator in financial_indicators) or
            (sector == 'financial services' and 
             any(indicator in industry.lower() for indicator in financial_indicators))
        )
        
        if is_financial_institution:
            non_compliant_reasons.append("Company operates in interest-based financial services")

        # Combined business compliance check
        is_business_compliant = len(non_compliant_reasons) == 0

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
            'non_compliant_reasons': non_compliant_reasons,
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
