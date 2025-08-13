import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import re

class StockDataFetcher:
    """Class to handle stock data fetching from Yahoo Finance"""
    
    def __init__(self):
        # Hong Kong stock exchange mapping
        self.hk_exchanges = {
            'main': '.HK',      # Main Board
            'gem': '.HK'        # GEM Board
        }
    
    def format_hk_symbol(self, symbol):
        """
        Format Hong Kong stock symbols for Yahoo Finance
        
        Args:
            symbol (str): Stock symbol (e.g., '0700', '700', '0001')
            
        Returns:
            str: Formatted symbol for Yahoo Finance (e.g., '0700.HK')
        """
        # Remove any existing exchange suffix
        symbol = symbol.upper().replace('.HK', '').replace('.HE', '')
        
        # Check if it's a numeric HK stock code
        if symbol.isdigit():
            # Pad with zeros to make it 4 digits
            symbol = symbol.zfill(4)
            return f"{symbol}.HK"
        
        return symbol
    
    def detect_market(self, symbol):
        """
        Detect which market the symbol belongs to
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Market information
        """
        symbol_clean = symbol.upper().replace('.HK', '').replace('.HE', '')
        
        # Hong Kong stocks (numeric codes)
        if symbol_clean.isdigit():
            return {
                'market': 'Hong Kong',
                'exchange': 'HKEX',
                'formatted_symbol': self.format_hk_symbol(symbol),
                'currency': 'HKD'
            }
        
        # US stocks (alphabetic symbols)
        elif symbol_clean.isalpha():
            return {
                'market': 'United States',
                'exchange': 'NASDAQ/NYSE',
                'formatted_symbol': symbol_clean,
                'currency': 'USD'
            }
        
        # Mixed or other formats
        else:
            return {
                'market': 'Other',
                'exchange': 'Various',
                'formatted_symbol': symbol,
                'currency': 'Various'
            }
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_stock_data(_self, symbol, period="1y"):
        """
        Fetch stock data and company information
        
        Args:
            symbol (str): Stock ticker symbol
            period (str): Time period for historical data
            
        Returns:
            tuple: (stock_data_df, stock_info_dict, market_info_dict) or (None, None, None) if error
        """
        try:
            # Detect market and format symbol
            market_info = _self.detect_market(symbol)
            formatted_symbol = market_info['formatted_symbol']
            
            # Create ticker object with formatted symbol
            ticker = yf.Ticker(formatted_symbol)
            
            # Get historical data
            stock_data = ticker.history(period=period)
            
            # Check if data is empty
            if stock_data.empty:
                st.error(f"No data found for symbol {formatted_symbol}")
                return None, None, None
            
            # Get company info
            try:
                stock_info = ticker.info
            except Exception as e:
                st.warning(f"Could not fetch company info: {e}")
                stock_info = {}
            
            # Ensure we have basic price data
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in stock_data.columns for col in required_columns):
                st.error("Incomplete price data received")
                return None, None, None
            
            # Clean the data
            stock_data = stock_data.dropna()
            
            # Add some basic calculated fields
            stock_data['Price_Change'] = stock_data['Close'].diff()
            stock_data['Price_Change_Pct'] = stock_data['Close'].pct_change() * 100
            
            return stock_data, stock_info, market_info
            
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return None, None, None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_company_financials(_self, symbol):
        """
        Get company financial statements
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Dictionary containing financial statements
        """
        try:
            ticker = yf.Ticker(symbol)
            
            financials = {
                'income_statement': ticker.financials,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow
            }
            
            return financials
            
        except Exception as e:
            st.warning(f"Could not fetch financial statements: {e}")
            return {}
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour  
    def get_analyst_info(_self, symbol):
        """
        Get analyst recommendations and price targets
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Dictionary containing analyst information
        """
        try:
            ticker = yf.Ticker(symbol)
            
            analyst_info = {
                'recommendations': ticker.recommendations,
                'calendar': ticker.calendar,
                'earnings': ticker.earnings
            }
            
            return analyst_info
            
        except Exception as e:
            st.warning(f"Could not fetch analyst information: {e}")
            return {}
    
    def validate_symbol(self, symbol):
        """
        Validate if a stock symbol exists
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            bool: True if symbol is valid, False otherwise
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got valid info back
            if 'symbol' in info or 'shortName' in info or 'longName' in info:
                return True
            return False
            
        except:
            return False
    
    def get_market_status(self):
        """
        Get current market status
        
        Returns:
            dict: Market status information
        """
        try:
            # Using SPY as a proxy for market status
            spy = yf.Ticker("SPY")
            info = spy.info
            
            market_status = {
                'market_state': info.get('marketState', 'Unknown'),
                'exchange_timezone': info.get('exchangeTimezoneName', 'Unknown'),
                'regular_market_time': info.get('regularMarketTime', None)
            }
            
            return market_status
            
        except Exception as e:
            return {'error': str(e)}
