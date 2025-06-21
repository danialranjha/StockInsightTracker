# Stock Insight Tracker

A Streamlit application for analyzing stock debt ratios and Islamic compliance screening.

## Features

- **Stock Analysis**: Calculate custom debt ratios (excluding goodwill and intangible assets)
- **Islamic Screening**: Comprehensive Shariah compliance analysis based on financial ratios and business activities
- **Visual Analytics**: Interactive charts and graphs powered by Plotly
- **Data Export**: Download analysis results as CSV files
- **Caching**: Intelligent caching system to reduce API calls and improve performance

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd stock-insight-tracker
```

2. Install dependencies:
```bash
# Using uv (recommended)
pip install uv
uv pip install -e ".[test]"

# Or using pip
pip install -e ".[test]"
```

## Usage

### Running the Application

```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501`

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run tests with detailed coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_stock_data.py

# Run tests in parallel
pytest -n auto
```

### Code Quality Checks

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Security scan
bandit -r .

# Check dependencies for vulnerabilities  
safety check
```

## Project Structure

```
├── main.py                 # Main Streamlit application
├── utils/                  # Utility modules
│   ├── calculations.py     # Financial calculations
│   ├── cache.py           # Caching utilities
│   ├── islamic_screening.py # Islamic compliance logic
│   └── stock_data.py      # Stock data fetching
├── tests/                 # Test suite
│   ├── test_calculations.py
│   ├── test_cache.py
│   ├── test_islamic_screening.py
│   └── test_stock_data.py
├── scripts/               # Utility scripts
├── .github/workflows/     # CI/CD workflows
└── pyproject.toml        # Project configuration
```

## Testing

This project maintains high test coverage (≥80%) with comprehensive test suites for all modules.

### Test Categories

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **Security Tests**: Automated security vulnerability scanning
- **Code Quality**: Linting, formatting, and complexity checks

### Continuous Integration

The project uses GitHub Actions for:

- **Automated Testing**: Runs on Python 3.11 and 3.12
- **Coverage Reporting**: Automatically generates and reports test coverage
- **Security Scanning**: Checks for vulnerabilities and security issues
- **Code Quality**: Enforces formatting and linting standards
- **PR Checks**: Validates pull requests before merging

### Branch Protection

The `main` branch is protected with the following requirements:

- ✅ All tests must pass
- ✅ Code coverage must be ≥80%
- ✅ Security scans must pass
- ✅ Code must be properly formatted
- ✅ At least 1 reviewer approval required
- ✅ Branch must be up to date before merging

## Islamic Screening Criteria

The application screens stocks based on:

### Financial Ratios (must be <33%)
- **Debt Ratio**: Long-term debt / Total assets
- **Liquidity Ratio**: Cash & equivalents / Market capitalization  
- **Receivables Ratio**: Accounts receivable / Market capitalization

### Business Activities
- Excludes companies involved in:
  - Financial services (banking, insurance)
  - Alcohol production/distribution
  - Gambling
  - Adult entertainment
  - Pork/non-halal food products
  - Military weapons

## Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
uv pip install -e ".[test]"
```

2. Set up pre-commit hooks (optional):
```bash
pip install pre-commit
pre-commit install
```

3. Run the development server:
```bash
streamlit run main.py
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Branch Protection Setup

To enable branch protection rules (requires admin access):

```bash
./setup-branch-protection.sh
```

This will configure:
- Required status checks
- Pull request reviews
- Branch update requirements
- Protection against force pushes

## API Rate Limiting

The application implements intelligent rate limiting and caching:

- **Request Caching**: 1-hour cache for yfinance API calls
- **Rate Limiting**: Automatic throttling to prevent 429 errors
- **Retry Logic**: Exponential backoff for failed requests
- **Custom User-Agent**: Identifies the application to API providers

## License

[Add your license information here]

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check existing issues for solutions
- Review the test suite for usage examples