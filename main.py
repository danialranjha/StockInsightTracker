import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.stock_data import get_stock_data, prepare_download_data
from utils.calculations import calculate_debt_ratio, format_currency

st.set_page_config(page_title="Stock Debt Analysis",
                   page_icon="📈",
                   layout="wide")

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
    </style>
    """,
            unsafe_allow_html=True)


def main():
    st.title("Stock Debt Analysis Dashboard")

    st.markdown("""
    This application analyzes stock data and calculates custom debt ratios, 
    excluding goodwill and intangible assets from the company's value.
    """)

    # User input
    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):", "").upper()

    if symbol:
        with st.spinner('Fetching data...'):
            hist_data, financial_data, info = get_stock_data(symbol)

            if hist_data is None or financial_data is None:
                st.error(
                    "Error fetching data. Please check the stock symbol and try again."
                )
                return

            # Calculate debt ratio
            debt_ratio = calculate_debt_ratio(financial_data)

            # Display company info
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"{info.get('longName', symbol)} ({symbol})")
                st.write(f"Sector: {info.get('sector', 'N/A')}")
            with col2:
                if debt_ratio:
                    ratio_color = "high-debt" if debt_ratio > 30 else "normal-debt"
                    st.markdown(
                        f"<h3>Debt Ratio: <span class='{ratio_color}'>{debt_ratio}%</span></h3>",
                        unsafe_allow_html=True)

            # Financial metrics table
            st.subheader("Financial Metrics")
            metrics_df = pd.DataFrame({
                'Metric': [
                    'Long Term Debt', 'Market Value', 'Goodwill',
                    'Intangible Assets'
                ],
                'Value': [
                    format_currency(financial_data['Long_Term_Debt']),
                    format_currency(financial_data['Market_Value']),
                    format_currency(financial_data['Goodwill']),
                    format_currency(financial_data['Intangible_Assets'])
                ]
            })
            st.table(metrics_df)

            # Create plots
            fig = make_subplots(rows=2,
                                cols=1,
                                shared_xaxes=True,
                                subplot_titles=('Stock Price',
                                                'Trading Volume'))

            fig.add_trace(go.Scatter(x=hist_data.index,
                                     y=hist_data['Close'],
                                     name="Stock Price",
                                     line=dict(color="#1f77b4")),
                          row=1,
                          col=1)

            fig.add_trace(go.Bar(x=hist_data.index,
                                 y=hist_data['Volume'],
                                 name="Volume",
                                 marker=dict(color="#2ca02c")),
                          row=2,
                          col=1)

            fig.update_layout(height=600, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            # Download button
            if st.button("Download Data as CSV"):
                df = prepare_download_data(hist_data, financial_data,
                                           debt_ratio)
                csv = df.to_csv(index=False)
                st.download_button(label="Click to Download",
                                   data=csv,
                                   file_name=f"{symbol}_analysis.csv",
                                   mime="text/csv")


if __name__ == "__main__":
    main()
