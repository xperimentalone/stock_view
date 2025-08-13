# Stock Analysis Dashboard

## Overview

This is a Streamlit-based stock analysis dashboard that provides comprehensive financial data visualization and analysis. The application fetches real-time stock data from Yahoo Finance and presents it through interactive charts, financial metrics, and relevant news. Users can analyze stock performance from both US and Hong Kong stock markets, view key financial indicators, explore historical price movements, and stay updated with market news through an intuitive web interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid dashboard development
- **Visualization**: Plotly for interactive charts and graphs including line charts, candlestick charts, and technical indicators
- **Styling**: Custom CSS embedded within Streamlit for enhanced UI appearance with metric cards and color-coded elements
- **Layout**: Wide layout configuration with expandable sidebar for controls and filters

### Backend Architecture
- **Modular Design**: Utility-based architecture with separate modules for different functionalities:
  - `data_fetcher.py`: Handles data retrieval, caching, and multi-market support (US & HK stocks)
  - `chart_utils.py`: Creates various chart types and visualizations
  - `financial_metrics.py`: Calculates and formats financial indicators
  - `news_fetcher.py`: Fetches relevant stock and market news from multiple sources
- **Multi-Market Support**: Automatic detection and formatting of US and Hong Kong stock symbols
- **Data Processing**: Pandas for data manipulation and NumPy for numerical computations
- **Session Management**: Streamlit session state for maintaining data across user interactions

### Data Storage Solutions
- **Caching Strategy**: Streamlit's built-in caching decorator (`@st.cache_data`) with 5-minute TTL to optimize API calls
- **In-Memory Storage**: Session state for temporary data persistence during user sessions
- **No Persistent Database**: Application relies on real-time data fetching without local data storage

### Technical Analysis Features
- **Price Charts**: Line charts with customizable moving averages and Bollinger bands
- **Financial Metrics**: Automated calculation of key indicators like P/E ratio, market cap, EPS, and price changes
- **Interactive Elements**: Plotly-powered charts with hover information and zoom capabilities
- **News Integration**: Real-time news feeds for specific stocks and general market updates
- **Multi-Currency Support**: Proper currency display for US (USD) and Hong Kong (HKD) markets
- **Excel Export**: Complete historical price data downloadable as formatted Excel files with metadata

## External Dependencies

### Data Providers
- **Yahoo Finance API**: Primary data source accessed through the `yfinance` Python library for real-time and historical stock data
- **Data Coverage**: Supports multiple time periods (1 day to multiple years) and comprehensive stock information including company fundamentals

### Third-Party Libraries
- **Streamlit**: Web application framework for the dashboard interface
- **Plotly**: Interactive visualization library for charts and graphs
- **yfinance**: Yahoo Finance API wrapper for stock data retrieval
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing for financial calculations
- **Feedparser**: RSS feed parsing for news aggregation
- **Trafilatura**: Web content extraction for news article processing
- **Requests**: HTTP library for web requests and API calls

### API Limitations
- **Rate Limiting**: Dependent on Yahoo Finance API availability and rate limits
- **Data Quality**: Subject to Yahoo Finance data accuracy and availability
- **Caching**: 5-minute cache TTL to balance data freshness with API usage efficiency
