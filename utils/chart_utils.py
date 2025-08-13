import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

class ChartCreator:
    """Class to create various types of financial charts"""
    
    def __init__(self):
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
    
    def create_line_chart(self, data, symbol, show_ma=False, show_bollinger=False):
        """
        Create a line chart for stock prices
        
        Args:
            data (DataFrame): Stock price data
            symbol (str): Stock symbol
            show_ma (bool): Whether to show moving averages
            show_bollinger (bool): Whether to show Bollinger bands
            
        Returns:
            plotly.graph_objects.Figure: Line chart figure
        """
        fig = go.Figure()
        
        # Add main price line
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color=self.colors['primary'], width=2),
            hovertemplate='<b>%{text}</b><br>' +
                         'Date: %{x}<br>' +
                         'Price: $%{y:.2f}<extra></extra>',
            text=[symbol] * len(data)
        ))
        
        # Add moving averages if requested
        if show_ma:
            self._add_moving_averages(fig, data)
        
        # Add Bollinger bands if requested
        if show_bollinger:
            self._add_bollinger_bands(fig, data)
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} Stock Price',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig
    
    def create_candlestick_chart(self, data, symbol, show_ma=False, show_bollinger=False):
        """
        Create a candlestick chart for stock prices
        
        Args:
            data (DataFrame): Stock price data with OHLC columns
            symbol (str): Stock symbol
            show_ma (bool): Whether to show moving averages
            show_bollinger (bool): Whether to show Bollinger bands
            
        Returns:
            plotly.graph_objects.Figure: Candlestick chart figure
        """
        fig = go.Figure()
        
        # Add candlestick trace
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'], 
            low=data['Low'],
            close=data['Close'],
            name=symbol,
            increasing_line_color=self.colors['success'],
            decreasing_line_color=self.colors['danger'],
            hoverinfo='all'
        ))
        
        # Add moving averages if requested
        if show_ma:
            self._add_moving_averages(fig, data)
        
        # Add Bollinger bands if requested
        if show_bollinger:
            self._add_bollinger_bands(fig, data)
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} Candlestick Chart',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white',
            height=600,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left", 
                x=0.01
            )
        )
        
        return fig
    
    def create_ohlc_chart(self, data, symbol, show_ma=False, show_bollinger=False):
        """
        Create an OHLC chart for stock prices
        
        Args:
            data (DataFrame): Stock price data with OHLC columns
            symbol (str): Stock symbol
            show_ma (bool): Whether to show moving averages
            show_bollinger (bool): Whether to show Bollinger bands
            
        Returns:
            plotly.graph_objects.Figure: OHLC chart figure
        """
        fig = go.Figure()
        
        # Add OHLC trace
        fig.add_trace(go.Ohlc(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'], 
            close=data['Close'],
            name=symbol,
            increasing_line_color=self.colors['success'],
            decreasing_line_color=self.colors['danger']
        ))
        
        # Add moving averages if requested
        if show_ma:
            self._add_moving_averages(fig, data)
        
        # Add Bollinger bands if requested
        if show_bollinger:
            self._add_bollinger_bands(fig, data)
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} OHLC Chart',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white',
            height=600,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig
    
    def add_volume_subplot(self, fig, data):
        """
        Add volume subplot to existing chart
        
        Args:
            fig (plotly.graph_objects.Figure): Existing chart figure
            data (DataFrame): Stock data with Volume column
            
        Returns:
            plotly.graph_objects.Figure: Chart with volume subplot
        """
        # Create subplot figure
        fig_with_volume = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Price', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # Add all traces from original figure to first subplot
        for trace in fig.data:
            fig_with_volume.add_trace(trace, row=1, col=1)
        
        # Add volume bar chart
        colors = [self.colors['success'] if close >= open_price 
                 else self.colors['danger'] 
                 for close, open_price in zip(data['Close'], data['Open'])]
        
        fig_with_volume.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7,
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Update layout
        fig_with_volume.update_layout(
            height=800,
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        # Update y-axis labels
        fig_with_volume.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig_with_volume.update_yaxes(title_text="Volume", row=2, col=1)
        fig_with_volume.update_xaxes(title_text="Date", row=2, col=1)
        
        return fig_with_volume
    
    def _add_moving_averages(self, fig, data):
        """Add moving average lines to chart"""
        # Calculate moving averages
        ma_20 = data['Close'].rolling(window=20).mean()
        ma_50 = data['Close'].rolling(window=50).mean()
        
        # Add MA20
        fig.add_trace(go.Scatter(
            x=data.index,
            y=ma_20,
            mode='lines',
            name='MA 20',
            line=dict(color=self.colors['warning'], width=1, dash='dash'),
            opacity=0.8
        ))
        
        # Add MA50
        fig.add_trace(go.Scatter(
            x=data.index,
            y=ma_50,
            mode='lines',
            name='MA 50',
            line=dict(color=self.colors['info'], width=1, dash='dash'),
            opacity=0.8
        ))
    
    def _add_bollinger_bands(self, fig, data):
        """Add Bollinger bands to chart"""
        # Calculate Bollinger bands
        period = 20
        std_dev = 2
        
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        # Add upper band
        fig.add_trace(go.Scatter(
            x=data.index,
            y=upper_band,
            mode='lines',
            name='BB Upper',
            line=dict(color=self.colors['secondary'], width=1, dash='dot'),
            opacity=0.6
        ))
        
        # Add lower band
        fig.add_trace(go.Scatter(
            x=data.index,
            y=lower_band,
            mode='lines',
            name='BB Lower',
            line=dict(color=self.colors['secondary'], width=1, dash='dot'),
            opacity=0.6,
            fill='tonexty',
            fillcolor='rgba(255, 127, 14, 0.1)'
        ))
    
    def create_performance_chart(self, data, symbol):
        """
        Create a performance comparison chart
        
        Args:
            data (DataFrame): Stock price data
            symbol (str): Stock symbol
            
        Returns:
            plotly.graph_objects.Figure: Performance chart
        """
        # Calculate cumulative returns
        returns = data['Close'].pct_change().fillna(0)
        cumulative_returns = (1 + returns).cumprod() - 1
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=cumulative_returns * 100,
            mode='lines',
            name=f'{symbol} Returns',
            line=dict(color=self.colors['primary'], width=2),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        fig.update_layout(
            title=f'{symbol} Cumulative Returns',
            xaxis_title='Date',
            yaxis_title='Cumulative Return (%)',
            template='plotly_white',
            height=400,
            hovermode='x unified'
        )
        
        return fig
