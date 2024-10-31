def calculate_debt_ratio(financial_data):
    """Calculate custom debt ratio excluding goodwill and intangibles."""
    long_term_debt = financial_data['Long_Term_Debt']
    market_value = financial_data['Market_Value']
    goodwill = financial_data['Goodwill']
    intangibles = financial_data['Intangible_Assets']

    adjusted_value = market_value - goodwill - intangibles

    if adjusted_value <= 0:
        return None

    debt_ratio = (long_term_debt / adjusted_value) * 100
    return round(debt_ratio, 2)


def format_currency(value):
    """Format large numbers to readable currency format."""
    if abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    else:
        return f"${value:,.2f}"
