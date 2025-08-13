import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FinancialMetrics:
    """Class to calculate and format financial metrics"""
    
    def __init__(self, stock_info, stock_data):
        """
        Initialize with stock information and data
        
        Args:
            stock_info (dict): Stock information from yfinance
            stock_data (DataFrame): Historical stock price data
        """
        self.stock_info = stock_info
        self.stock_data = stock_data
    
    def get_key_metrics(self):
        """
        Get key financial metrics
        
        Returns:
            DataFrame: Key financial metrics
        """
        metrics = []
        
        # Price metrics
        current_price = self.stock_data['Close'].iloc[-1]
        metrics.append({"Metric": "Current Price", "Value": f"${current_price:.2f}"})
        
        # Market Cap
        market_cap = self.stock_info.get('marketCap')
        if market_cap:
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"${market_cap/1e6:.2f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"
            metrics.append({"Metric": "Market Cap", "Value": market_cap_str})
        
        # P/E Ratio
        pe_ratio = self.stock_info.get('trailingPE')
        if pe_ratio:
            metrics.append({"Metric": "P/E Ratio", "Value": f"{pe_ratio:.2f}"})
        
        # EPS
        eps = self.stock_info.get('trailingEps')
        if eps:
            metrics.append({"Metric": "EPS (TTM)", "Value": f"${eps:.2f}"})
        
        # Dividend Yield
        dividend_yield = self.stock_info.get('dividendYield')
        if dividend_yield:
            metrics.append({"Metric": "Dividend Yield", "Value": f"{dividend_yield*100:.2f}%"})
        
        # Book Value
        book_value = self.stock_info.get('bookValue')
        if book_value:
            metrics.append({"Metric": "Book Value", "Value": f"${book_value:.2f}"})
        
        # Price to Book
        price_to_book = self.stock_info.get('priceToBook')
        if price_to_book:
            metrics.append({"Metric": "Price/Book", "Value": f"{price_to_book:.2f}"})
        
        # 52 Week High/Low
        fifty_two_week_high = self.stock_info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = self.stock_info.get('fiftyTwoWeekLow')
        if fifty_two_week_high:
            metrics.append({"Metric": "52W High", "Value": f"${fifty_two_week_high:.2f}"})
        if fifty_two_week_low:
            metrics.append({"Metric": "52W Low", "Value": f"${fifty_two_week_low:.2f}"})
        
        # Beta
        beta = self.stock_info.get('beta')
        if beta:
            metrics.append({"Metric": "Beta", "Value": f"{beta:.2f}"})
        
        # Average Volume
        avg_volume = self.stock_info.get('averageVolume')
        if avg_volume:
            if avg_volume >= 1e6:
                volume_str = f"{avg_volume/1e6:.2f}M"
            elif avg_volume >= 1e3:
                volume_str = f"{avg_volume/1e3:.2f}K"
            else:
                volume_str = f"{avg_volume:,.0f}"
            metrics.append({"Metric": "Avg Volume", "Value": volume_str})
        
        return pd.DataFrame(metrics)
    
    def get_performance_metrics(self):
        """
        Calculate performance metrics for different time periods
        
        Returns:
            DataFrame: Performance metrics
        """
        performance = []
        current_price = self.stock_data['Close'].iloc[-1]
        
        # Define time periods
        periods = {
            "1 Day": 1,
            "1 Week": 5,
            "1 Month": 21,
            "3 Months": 63,
            "6 Months": 126,
            "1 Year": 252,
            "YTD": None  # Year to date
        }
        
        for period_name, days in periods.items():
            try:
                if period_name == "YTD":
                    # Calculate YTD performance
                    current_year = datetime.now().year
                    ytd_data = self.stock_data[self.stock_data.index.year == current_year]
                    if len(ytd_data) > 0:
                        start_price = ytd_data['Close'].iloc[0]
                        change_pct = ((current_price - start_price) / start_price) * 100
                    else:
                        change_pct = 0
                else:
                    # Calculate performance for specific number of days
                    if len(self.stock_data) > days:
                        start_price = self.stock_data['Close'].iloc[-days-1]
                        change_pct = ((current_price - start_price) / start_price) * 100
                    else:
                        # Not enough data for this period
                        continue
                
                # Format the return value
                if change_pct > 0:
                    return_str = f"+{change_pct:.2f}%"
                else:
                    return_str = f"{change_pct:.2f}%"
                
                performance.append({
                    "Period": period_name,
                    "Return": return_str
                })
                
            except Exception:
                continue
        
        return pd.DataFrame(performance)
    
    def get_volatility_metrics(self):
        """
        Calculate volatility and risk metrics
        
        Returns:
            dict: Volatility metrics
        """
        # Calculate daily returns
        returns = self.stock_data['Close'].pct_change().dropna()
        
        # Volatility (annualized)
        daily_volatility = returns.std()
        annualized_volatility = daily_volatility * np.sqrt(252)
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        excess_returns = returns.mean() * 252 - risk_free_rate
        sharpe_ratio = excess_returns / annualized_volatility if annualized_volatility != 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns, 5)
        
        return {
            'annualized_volatility': annualized_volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,
            'var_95': var_95 * 100
        }
    
    def get_technical_indicators(self):
        """
        Calculate technical indicators
        
        Returns:
            dict: Technical indicators
        """
        close_prices = self.stock_data['Close']
        
        # RSI (14-day)
        rsi = self._calculate_rsi(close_prices, 14)
        
        # MACD
        macd, macd_signal, macd_histogram = self._calculate_macd(close_prices)
        
        # Bollinger Bands position
        bb_position = self._calculate_bollinger_position(close_prices)
        
        return {
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'bollinger_position': bb_position
        }
    
    def _calculate_rsi(self, prices, window=14):
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else None
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        
        return (
            macd.iloc[-1] if not macd.empty else None,
            macd_signal.iloc[-1] if not macd_signal.empty else None,
            macd_histogram.iloc[-1] if not macd_histogram.empty else None
        )
    
    def _calculate_bollinger_position(self, prices, window=20, num_std=2):
        """Calculate position within Bollinger Bands"""
        sma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        current_price = prices.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        
        if pd.isna(current_upper) or pd.isna(current_lower):
            return None
        
        # Position as percentage (0 = lower band, 50 = middle, 100 = upper band)
        position = ((current_price - current_lower) / (current_upper - current_lower)) * 100
        return position
    
    def format_number(self, number, format_type="currency"):
        """
        Format numbers for display
        
        Args:
            number: Number to format
            format_type: Type of formatting (currency, percentage, number)
            
        Returns:
            str: Formatted number string
        """
        if pd.isna(number) or number is None:
            return "N/A"
        
        if format_type == "currency":
            if abs(number) >= 1e12:
                return f"${number/1e12:.2f}T"
            elif abs(number) >= 1e9:
                return f"${number/1e9:.2f}B"
            elif abs(number) >= 1e6:
                return f"${number/1e6:.2f}M"
            elif abs(number) >= 1e3:
                return f"${number/1e3:.2f}K"
            else:
                return f"${number:.2f}"
        
        elif format_type == "percentage":
            return f"{number:.2f}%"
        
        elif format_type == "number":
            if abs(number) >= 1e9:
                return f"{number/1e9:.2f}B"
            elif abs(number) >= 1e6:
                return f"{number/1e6:.2f}M"
            elif abs(number) >= 1e3:
                return f"{number/1e3:.2f}K"
            else:
                return f"{number:,.0f}"
        
        else:
            return str(number)
