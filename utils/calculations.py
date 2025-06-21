def calculate_debt_ratio(financial_data):
    """Calculate custom debt ratio excluding goodwill and intangibles."""
    if not financial_data:
        return None

    long_term_debt = financial_data.get("Long_Term_Debt", 0)
    total_assets = financial_data.get("Total_Assets", 0)
    goodwill_and_intangibles = financial_data.get("Goodwill_And_Intangibles", 0)

    # Handle None values
    if long_term_debt is None:
        long_term_debt = 0
    if total_assets is None:
        return None
    if goodwill_and_intangibles is None:
        goodwill_and_intangibles = 0

    adjusted_value = total_assets - goodwill_and_intangibles

    if adjusted_value <= 0:
        return None

    debt_ratio = (long_term_debt / adjusted_value) * 100
    return round(debt_ratio, 2)


def format_currency(value):
    """Format large numbers to readable currency format."""
    if value is None:
        return "N/A"

    # Convert string to number if needed
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return "N/A"

    if abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    else:
        return f"${value:,.0f}"
