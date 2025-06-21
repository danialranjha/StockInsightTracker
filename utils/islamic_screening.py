import logging
from utils.calculations import calculate_debt_ratio

def calculate_ratios(financial_data, info):
    """Calculate financial ratios for Islamic compliance."""
    debt_ratio = calculate_debt_ratio(financial_data)
    
    liquidity_ratio = 0
    receivables_ratio = 0
    is_debt_compliant = False
    is_liquidity_compliant = True  # Default to True if we can't calculate
    is_receivables_compliant = True  # Default to True if we can't calculate
    
    market_cap = info.get('marketCap', 0)
    if market_cap > 0:
        cash_and_investments = sum([
            info.get('totalCash', 0),
            info.get('shortTermInvestments', 0),
            info.get('longTermInvestments', 0)
        ])
        accounts_receivable = info.get('netReceivables', 0)

        liquidity_ratio = (cash_and_investments / market_cap) * 100
        receivables_ratio = (accounts_receivable / market_cap) * 100

        is_liquidity_compliant = liquidity_ratio < 33
        is_receivables_compliant = receivables_ratio < 33
    
    if debt_ratio is not None:
        is_debt_compliant = debt_ratio < 33

    return {
        'debt_ratio': round(debt_ratio, 2),
        'liquidity_ratio': round(liquidity_ratio, 2),
        'receivables_ratio': round(receivables_ratio, 2),
        'is_debt_compliant': is_debt_compliant,
        'is_liquidity_compliant': is_liquidity_compliant,
        'is_receivables_compliant': is_receivables_compliant
    }

def check_business_practices(info):
    """Check business practices for Islamic compliance."""
    logging.basicConfig(level=logging.DEBUG)
    sector = info.get('sector', '').lower()
    industry = info.get('industry', '')
    company_name = info.get('longName', '').lower()
    business_summary = info.get('longBusinessSummary', '').lower()

    logging.debug(f"Checking business practices for: {company_name}")
    logging.debug(f"Sector: {sector}, Industry: {industry}")
    logging.debug(f"Business Summary: {business_summary}")

    non_compliant_categories = {
        'alcohol': [
            'alcohol', 'brewery', 'breweries', 'distillery', 'distilleries', 
            'wine', 'spirits', 'beer', 'liquor', 'beverages-alcoholic',
            'craft brew', 'craft beer', 'wines & spirits', 'winery',
            'brewing', 'alcoholic beverages', 'malt beverages',
            'beverage-brewers', 'beverage distribution-alcohol',
            'beverages - brewers', 'beverages - wineries & distilleries',
            'brewing company', 'brewers', 'brewer', 'anheuser', 'busch',
            'heineken', 'carlsberg', 'molson', 'coors', 'budweiser',
            'corona', 'stella artois', 'draft beer', 'pale ale', 'lager'
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
            'credit card company', 'credit card issuer', 'credit card provider',
            'credit card business', 'credit card services', 'credit card processing',
            'lending services', 'consumer lending', 'asset management', 
            'capital markets', 'insurance', 'investment brokerage', 
            'wealth management', 'retail banking', 'corporate banking', 
            'financial exchange'
        ]
    }

    alcohol_industries = [
        'beverages - brewers',
        'beverages - wineries & distilleries',
        'alcoholic beverages',
        'brewery companies',
        'beverages-brewers',
        'brewers'
    ]

    non_compliant_reasons = []
    
    if any(industry.lower() == alcohol_ind.lower() for alcohol_ind in alcohol_industries):
        reason = f"Company is in the {industry} industry"
        non_compliant_reasons.append(reason)
        logging.debug(reason)
    
    for category, keywords in non_compliant_categories.items():
        if any(keyword in company_name for keyword in keywords):
            reason = f"Company name indicates involvement in {category} business"
            if reason not in non_compliant_reasons:
                non_compliant_reasons.append(reason)
                logging.debug(reason)
        
        if any(keyword in industry.lower() for keyword in keywords):
            reason = f"Company operates in {category} industry"
            if reason not in non_compliant_reasons:
                non_compliant_reasons.append(reason)
                logging.debug(reason)
        
        if any(keyword in business_summary for keyword in keywords):
            reason = f"Company's business description indicates involvement in {category}"
            if reason not in non_compliant_reasons:
                non_compliant_reasons.append(reason)
                logging.debug(reason)
        
        if any(keyword in sector for keyword in keywords):
            reason = f"Company operates in {category} sector"
            if reason not in non_compliant_reasons:
                non_compliant_reasons.append(reason)
                logging.debug(reason)

    financial_indicators = [
        'bank', 'banking', 'credit union', 'savings and loan',
        'mortgage reit', 'financial exchange', 'insurance carrier',
        'investment brokerage', 'asset management', 'wealth management'
    ]

    is_financial_institution = (
        any(indicator in industry.lower() for indicator in financial_indicators) or
        any(indicator in company_name for indicator in financial_indicators) or
        (sector == 'financial services' and 
         any(indicator in industry.lower() for indicator in financial_indicators))
    )
    
    if is_financial_institution:
        reason = "Company operates in interest-based financial services"
        non_compliant_reasons.append(reason)
        logging.debug(reason)

    is_business_compliant = len(non_compliant_reasons) == 0

    return {
        'is_business_compliant': is_business_compliant,
        'non_compliant_reasons': non_compliant_reasons
    }

def calculate_islamic_ratios(financial_data, info):
    """Calculate Islamic compliance ratios and check business practices."""
    try:
        ratios = calculate_ratios(financial_data, info)
        business_practices = check_business_practices(info)

        return {
            **ratios,
            **business_practices,
            'is_fully_compliant': (
                ratios['is_debt_compliant'] and 
                ratios['is_liquidity_compliant'] and 
                ratios['is_receivables_compliant'] and 
                business_practices['is_business_compliant']
            )
        }
    except Exception as e:
        print(f"Error in Islamic screening calculations: {str(e)}")
        return None
