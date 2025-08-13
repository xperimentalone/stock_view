import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from utils.data_fetcher import StockDataFetcher
from utils.chart_utils import ChartCreator
from utils.financial_metrics import FinancialMetrics
from utils.news_fetcher import NewsFetcher
import io

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .neutral {
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

def create_excel_download(stock_data, symbol, market_info):
    """
    Create Excel file with historical stock data
    
    Args:
        stock_data (DataFrame): Stock price data
        symbol (str): Stock symbol
        market_info (dict): Market information
        
    Returns:
        bytes: Excel file content as bytes
    """
    # Prepare data for Excel
    excel_data = stock_data.copy()
    excel_data.index.name = 'Date'
    
    # Reset index to make date a column
    excel_data = excel_data.reset_index()
    excel_data['Date'] = excel_data['Date'].dt.strftime('%Y-%m-%d')
    
    # Add percentage change column
    excel_data['Change %'] = excel_data['Close'].pct_change() * 100
    excel_data['Change %'] = excel_data['Change %'].round(2)
    
    # Reorder columns
    column_order = ['Date', 'Open', 'High', 'Low', 'Close', 'Change %', 'Volume', 'Price_Change', 'Price_Change_Pct']
    excel_data = excel_data[[col for col in column_order if col in excel_data.columns]]
    
    # Round numerical columns
    numerical_columns = ['Open', 'High', 'Low', 'Close', 'Price_Change', 'Price_Change_Pct']
    for col in numerical_columns:
        if col in excel_data.columns:
            excel_data[col] = excel_data[col].round(2)
    
    # Create Excel file in memory
    output = io.BytesIO()
    
    # Create ExcelWriter with BytesIO buffer
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    try:
        # Write the main data
        excel_data.to_excel(writer, sheet_name='Historical Data', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Historical Data']
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Format headers
        for col_num, value in enumerate(excel_data.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 12)  # Date
        worksheet.set_column('B:F', 10)  # Price columns
        worksheet.set_column('G:G', 15)  # Volume
        worksheet.set_column('H:I', 12)  # Change columns
        
        # Add metadata sheet
        metadata = pd.DataFrame({
            'Property': ['Symbol', 'Company Name', 'Market', 'Currency', 'Data Export Date', 'Total Records'],
            'Value': [
                symbol,
                market_info.get('company_name', 'N/A'),
                market_info.get('market', 'N/A'),
                market_info.get('currency', 'N/A'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                len(excel_data)
            ]
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
    finally:
        writer.close()
    
    return output.getvalue()

def main():
    st.title("📈 Stock Analysis Dashboard")
    st.markdown("### Comprehensive Financial Data and Interactive Charts")
    
    # Initialize session state
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = None
    if 'stock_info' not in st.session_state:
        st.session_state.stock_info = None
    
    # Sidebar for input controls
    with st.sidebar:
        st.header("📊 Analysis Controls")
        
        # Stock symbol input
        stock_symbol = st.text_input(
            "Enter Stock Symbol",
            placeholder="e.g., AAPL, GOOGL, 0700, 0001",
            help="Enter a stock ticker symbol (US: AAPL, GOOGL; HK: 0700, 0001)"
        ).upper()
        
        # Time period selection
        period_options = {
            "1 Month": "1mo",
            "3 Months": "3mo", 
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }
        
        selected_period = st.selectbox(
            "Select Time Period",
            options=list(period_options.keys()),
            index=3  # Default to 1 Year
        )
        
        # Chart type selection
        chart_type = st.selectbox(
            "Chart Type",
            options=["Line Chart", "Candlestick Chart", "OHLC Chart"],
            index=0
        )
        
        # Technical indicators
        st.subheader("Technical Indicators")
        show_ma = st.checkbox("Moving Averages (20, 50)")
        show_volume = st.checkbox("Volume", value=True)
        show_bollinger = st.checkbox("Bollinger Bands")
        
        # Fetch data button
        if st.button("🔍 Analyze Stock", type="primary"):
            if stock_symbol:
                with st.spinner(f"Fetching data for {stock_symbol}..."):
                    data_fetcher = StockDataFetcher()
                    stock_data, stock_info, market_info = data_fetcher.get_stock_data(
                        stock_symbol, 
                        period_options[selected_period]
                    )
                    
                    if stock_data is not None and not stock_data.empty:
                        st.session_state.stock_data = stock_data
                        st.session_state.stock_info = stock_info
                        st.session_state.market_info = market_info
                        st.session_state.symbol = stock_symbol
                        st.success(f"✅ Data loaded successfully for {stock_symbol} ({market_info['market']} Market)")
                    else:
                        st.error(f"❌ Unable to fetch data for {stock_symbol}. Please check the symbol and try again.")
            else:
                st.warning("⚠️ Please enter a stock symbol")
    
    # Main content area
    if st.session_state.stock_data is not None and st.session_state.stock_info is not None:
        stock_data = st.session_state.stock_data
        stock_info = st.session_state.stock_info
        market_info = st.session_state.get('market_info', {})
        symbol = st.session_state.symbol
        
        # Stock header with current price
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            company_name = stock_info.get('longName', symbol)
            market_name = market_info.get('market', 'Unknown')
            currency = market_info.get('currency', 'USD')
            st.markdown(f"## {company_name} ({symbol})")
            st.caption(f"📍 {market_name} Market • {currency}")
            
        current_price = stock_data['Close'].iloc[-1]
        previous_close = stock_info.get('previousClose', stock_data['Close'].iloc[-2])
        price_change = current_price - previous_close
        price_change_pct = (price_change / previous_close) * 100
        
        with col2:
            currency_symbol = "$" if currency == "USD" else f"{currency} " if currency == "HKD" else "$"
            st.metric(
                "Current Price",
                f"{currency_symbol}{current_price:.2f}",
                f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
            )
            
        with col3:
            market_cap = stock_info.get('marketCap', 0)
            if market_cap > 0:
                market_cap_formatted = f"${market_cap/1e9:.2f}B" if market_cap >= 1e9 else f"${market_cap/1e6:.2f}M"
                st.metric("Market Cap", market_cap_formatted)
                
        with col4:
            volume = stock_data['Volume'].iloc[-1]
            avg_volume = stock_info.get('averageVolume', 0)
            volume_formatted = f"{volume/1e6:.2f}M" if volume >= 1e6 else f"{volume/1e3:.2f}K"
            st.metric("Volume", volume_formatted)
        
        # Charts section
        st.markdown("---")
        
        # Create charts
        chart_creator = ChartCreator()
        
        if chart_type == "Line Chart":
            fig = chart_creator.create_line_chart(
                stock_data, symbol, show_ma, show_bollinger
            )
        elif chart_type == "Candlestick Chart":
            fig = chart_creator.create_candlestick_chart(
                stock_data, symbol, show_ma, show_bollinger
            )
        else:  # OHLC Chart
            fig = chart_creator.create_ohlc_chart(
                stock_data, symbol, show_ma, show_bollinger
            )
        
        # Add volume subplot if requested
        if show_volume:
            fig = chart_creator.add_volume_subplot(fig, stock_data)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Financial metrics and data tables
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Key Financial Metrics")
            
            financial_metrics = FinancialMetrics(stock_info, stock_data)
            metrics_df = financial_metrics.get_key_metrics()
            
            # Display metrics in a nice format
            for index, row in metrics_df.iterrows():
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**{row['Metric']}**")
                with col_b:
                    st.markdown(f"{row['Value']}")
        
        with col2:
            st.subheader("📈 Performance Analysis")
            
            performance_df = financial_metrics.get_performance_metrics()
            
            for index, row in performance_df.iterrows():
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**{row['Period']}**")
                with col_b:
                    value = row['Return']
                    color = "positive" if "+" in str(value) else "negative" if "-" in str(value) else "neutral"
                    st.markdown(f"<span class='{color}'>{value}</span>", unsafe_allow_html=True)
        
        # Historical data download
        st.markdown("---")
        st.subheader("📋 Historical Price Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Data Range:** {stock_data.index.min().strftime('%Y-%m-%d')} to {stock_data.index.max().strftime('%Y-%m-%d')}")
            st.write(f"**Total Records:** {len(stock_data)} trading days")
            st.write(f"**Market:** {market_info.get('market', 'Unknown')} ({market_info.get('currency', 'USD')})")
        
        with col2:
            # Add company name to market_info for Excel metadata
            enhanced_market_info = market_info.copy()
            enhanced_market_info['company_name'] = stock_info.get('longName', symbol)
            
            # Generate Excel file
            excel_data = create_excel_download(stock_data, symbol, enhanced_market_info)
            
            # Create download button
            filename = f"{symbol}_historical_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
            st.download_button(
                label="📥 Download Excel File",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                help="Download complete historical price data as Excel file"
            )
        
        # Show preview of recent data
        st.markdown("**📈 Recent Price Data (Last 10 Days)**")
        preview_data = stock_data.tail(10).copy()
        preview_data.index = preview_data.index.strftime('%Y-%m-%d')
        preview_data = preview_data.round(2)
        
        # Add percentage change column for preview
        preview_data['Change %'] = preview_data['Close'].pct_change() * 100
        preview_data['Change %'] = preview_data['Change %'].round(2)
        
        # Reorder columns for preview
        preview_columns = ['Open', 'High', 'Low', 'Close', 'Change %', 'Volume']
        preview_display = preview_data[preview_columns]
        
        st.dataframe(preview_display, use_container_width=True)
        
        # Company information
        st.markdown("---")
        st.subheader("🏢 Company Information")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            if 'longBusinessSummary' in stock_info:
                st.markdown("**Business Summary:**")
                st.write(stock_info['longBusinessSummary'][:500] + "..." if len(stock_info['longBusinessSummary']) > 500 else stock_info['longBusinessSummary'])
        
        with info_col2:
            st.markdown("**Company Details:**")
            details = {
                "Sector": stock_info.get('sector', 'N/A'),
                "Industry": stock_info.get('industry', 'N/A'),
                "Country": stock_info.get('country', 'N/A'),
                "Employees": stock_info.get('fullTimeEmployees', 'N/A'),
                "Website": stock_info.get('website', 'N/A')
            }
            
            for key, value in details.items():
                if value != 'N/A':
                    if key == "Employees" and isinstance(value, (int, float)):
                        value = f"{value:,}"
                    st.write(f"**{key}:** {value}")
        
        # News section
        st.markdown("---")
        st.subheader("📰 Related News")
        
        # Fetch and display news
        with st.spinner("Loading latest news..."):
            news_fetcher = NewsFetcher()
            
            # Get stock-specific news
            company_name = stock_info.get('longName', stock_info.get('shortName', ''))
            stock_news = news_fetcher.get_stock_news(symbol, company_name, max_articles=3)
            
            # Get market news (HK specific if it's a HK stock)
            if market_info.get('market') == 'Hong Kong':
                market_news = news_fetcher.get_hk_market_news(max_articles=3)
            else:
                market_news = news_fetcher.get_market_news(max_articles=3)
        
        # Display news in tabs
        if stock_news or market_news:
            tab1, tab2 = st.tabs([f"📈 {symbol} News", "🌐 Market News"])
            
            with tab1:
                if stock_news:
                    for article in stock_news:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**[{article['title']}]({article['link']})**")
                                if article['summary']:
                                    st.write(article['summary'])
                            with col2:
                                st.caption(f"📅 {news_fetcher.format_time_ago(article['published'])}")
                                st.caption(f"📰 {article['source']}")
                            st.markdown("---")
                else:
                    st.info("No specific news found for this stock.")
            
            with tab2:
                if market_news:
                    for article in market_news:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**[{article['title']}]({article['link']})**")
                                if article['summary']:
                                    st.write(article['summary'])
                            with col2:
                                st.caption(f"📅 {news_fetcher.format_time_ago(article['published'])}")
                                st.caption(f"📰 {article['source']}")
                            st.markdown("---")
                else:
                    st.info("No market news available at the moment.")
        else:
            st.info("No news available at the moment. Please try again later.")
    
    else:
        # Welcome screen
        st.markdown("""
        ## Welcome to the Stock Analysis Dashboard! 👋
        
        Get started by:
        1. 📝 Enter a stock symbol in the sidebar (US: AAPL, GOOGL; HK: 0700, 0001)
        2. ⏱️ Select your preferred time period
        3. 📊 Choose chart type and technical indicators
        4. 🔍 Click "Analyze Stock" to fetch data
        
        ### Features:
        - 📈 Interactive price charts with multiple visualizations
        - 💰 Real-time stock prices and key financial metrics
        - 📊 Technical indicators (Moving averages, Bollinger bands)
        - 📥 Excel download for complete historical price data
        - 🏢 Company information and business summary
        - 📰 Related news and market updates
        - 📱 Responsive design for all devices
        
        ### Supported Stock Exchanges:
        - 🇺🇸 US Markets: NASDAQ, NYSE, AMEX
        - 🇭🇰 Hong Kong Stock Exchange (HKEX)
        - 🌍 Major international exchanges
        - 💱 Currency pairs and commodities
        """)
        
        # Sample symbols for quick access
        st.markdown("### 🚀 Popular Stocks to Try:")
        
        # US Stocks
        st.markdown("#### 🇺🇸 US Stocks")
        col1, col2, col3, col4 = st.columns(4)
        
        us_stocks = [
            ("AAPL", "Apple Inc."),
            ("GOOGL", "Alphabet Inc."),
            ("MSFT", "Microsoft Corp."),
            ("TSLA", "Tesla Inc."),
            ("AMZN", "Amazon.com Inc."),
            ("META", "Meta Platforms"),
            ("NVDA", "NVIDIA Corp."),
            ("NFLX", "Netflix Inc.")
        ]
        
        for i, (symbol, name) in enumerate(us_stocks):
            col = [col1, col2, col3, col4][i % 4]
            with col:
                st.markdown(f"**{symbol}** - {name}")
        
        # Hong Kong Stocks
        st.markdown("#### 🇭🇰 Hong Kong Stocks")
        col1, col2, col3, col4 = st.columns(4)
        
        hk_stocks = [
            ("0700", "騰訊控股 (Tencent)"),
            ("0005", "滙豐控股 (HSBC)"),
            ("0001", "長和 (CK Hutchison)"),
            ("0941", "中國移動 (China Mobile)"),
            ("0175", "吉利汽車 (Geely Auto)"),
            ("0027", "銀河娛樂 (Galaxy Ent)"),
            ("0883", "中國海洋石油 (CNOOC)"),
            ("2318", "中國平安 (Ping An)")
        ]
        
        for i, (symbol, name) in enumerate(hk_stocks):
            col = [col1, col2, col3, col4][i % 4]
            with col:
                st.markdown(f"**{symbol}** - {name}")

if __name__ == "__main__":
    main()
