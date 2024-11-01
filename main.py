import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.stock_data import get_stock_data, prepare_download_data
from utils.calculations import calculate_debt_ratio, format_currency
from utils.islamic_screening import calculate_islamic_ratios

st.set_page_config(
    page_title="Stock Debt Analysis",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .high-debt {
        color: #ff4b4b;
        font-weight: bold;
    }
    .normal-debt {
        color: #0f9d58;
        font-weight: bold;
    }
    .compliant {
        color: #0f9d58;
        font-weight: bold;
    }
    .non-compliant {
        color: #ff4b4b;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("Stock Debt Analysis Dashboard")
    
    st.markdown("""
    This application analyzes stock data and calculates:
    1. Custom debt ratios (excluding goodwill and intangible assets)
    2. Islamic compliance screening based on financial ratios and business activities
    """)
    
    # User input
    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):", "").upper()
    
    if symbol:
        with st.spinner('Fetching data...'):
            hist_data, financial_data, info = get_stock_data(symbol)
            
            if hist_data is None or financial_data is None:
                st.error("Error fetching data. Please check the stock symbol and try again.")
                return
                
            # Calculate debt ratio
            debt_ratio = calculate_debt_ratio(financial_data)
            
            # Calculate Islamic screening ratios
            islamic_ratios = calculate_islamic_ratios(financial_data, info)
            
            # Display company info
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"{info.get('longName', symbol)} ({symbol})")
                st.write(f"Sector: {info.get('sector', 'N/A')}")
                st.write(f"Industry: {info.get('industry', 'N/A')}")
            with col2:
                if debt_ratio:
                    ratio_color = "high-debt" if debt_ratio > 30 else "normal-debt"
                    st.markdown(f"<h3>Debt Ratio: <span class='{ratio_color}'>{debt_ratio}%</span></h3>", 
                              unsafe_allow_html=True)
            
            # Islamic Screening Results
            st.subheader("Islamic Screening Analysis")
            if islamic_ratios:
                # Overall compliance status
                compliance_status = "compliant" if islamic_ratios['is_fully_compliant'] else "non-compliant"
                st.markdown(f"<h3>Overall Status: <span class='{compliance_status}'>{'✓ Shariah Compliant' if islamic_ratios['is_fully_compliant'] else '✗ Non-Compliant'}</span></h3>", 
                          unsafe_allow_html=True)

                # Display detailed ratios
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    status = "compliant" if islamic_ratios['is_debt_compliant'] else "non-compliant"
                    st.markdown(f"Debt Ratio: <span class='{status}'>{islamic_ratios['debt_ratio']}%</span>", 
                              unsafe_allow_html=True)
                    st.markdown("Target: <33%")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    status = "compliant" if islamic_ratios['is_liquidity_compliant'] else "non-compliant"
                    st.markdown(f"Liquidity Ratio: <span class='{status}'>{islamic_ratios['liquidity_ratio']}%</span>", 
                              unsafe_allow_html=True)
                    st.markdown("Target: <33%")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col3:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    status = "compliant" if islamic_ratios['is_receivables_compliant'] else "non-compliant"
                    st.markdown(f"Receivables Ratio: <span class='{status}'>{islamic_ratios['receivables_ratio']}%</span>", 
                              unsafe_allow_html=True)
                    st.markdown("Target: <33%")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Business Activity Compliance
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                status = "compliant" if islamic_ratios['is_business_compliant'] else "non-compliant"
                st.markdown(f"Business Activities: <span class='{status}'>{'✓ Compliant' if islamic_ratios['is_business_compliant'] else '✗ Non-Compliant'}</span>", 
                          unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Financial metrics table
            st.subheader("Financial Metrics")
            metrics_df = pd.DataFrame({
                'Metric': ['Long Term Debt', 'Total Assets', 'Goodwill and Intangible Assets'],
                'Value': [
                    format_currency(financial_data['Long_Term_Debt']),
                    format_currency(financial_data['Total_Assets']),
                    format_currency(financial_data['Goodwill_And_Intangibles'])
                ]
            })
            st.table(metrics_df)
            
            # Create plots
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              subplot_titles=('Stock Price', 'Trading Volume'))
            
            fig.add_trace(
                go.Scatter(x=hist_data.index, y=hist_data['Close'],
                          name="Stock Price", line=dict(color="#1f77b4")),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=hist_data.index, y=hist_data['Volume'],
                      name="Volume", marker=dict(color="#2ca02c")),
                row=2, col=1
            )
            
            fig.update_layout(height=600, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # Download button
            if st.button("Download Data as CSV"):
                df = prepare_download_data(hist_data, financial_data, debt_ratio)
                # Add Islamic screening results
                if islamic_ratios:
                    df['Islamic_Compliance'] = islamic_ratios['is_fully_compliant']
                    df['Islamic_Debt_Ratio'] = islamic_ratios['debt_ratio']
                    df['Islamic_Liquidity_Ratio'] = islamic_ratios['liquidity_ratio']
                    df['Islamic_Receivables_Ratio'] = islamic_ratios['receivables_ratio']
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Click to Download",
                    data=csv,
                    file_name=f"{symbol}_analysis.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
