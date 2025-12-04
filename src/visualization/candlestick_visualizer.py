"""
Candlestick Visualizer Module

This module provides interactive candlestick chart visualization for stock data.
Supports multiple timeframes: daily, weekly, monthly, quarterly, and yearly.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List, Union
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class CandlestickVisualizer:
    """
    Interactive candlestick chart visualizer for stock data.
    
    Features:
    - Multiple timeframes (day, week, month, quarter, year)
    - Interactive zoom, pan, and hover
    - Volume overlay
    - Moving average overlays
    - Customizable appearance
    """
    
    def __init__(self, data: pd.DataFrame, symbol: str = "Stock"):
        """
        Initialize the CandlestickVisualizer.
        
        Args:
            data: DataFrame with columns: Date, Open, High, Low, Close, Volume
            symbol: Stock symbol or name for chart title
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        self.data = data.copy()
        self.symbol = symbol
        
        # Ensure Date is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.data['Date']):
            self.data['Date'] = pd.to_datetime(self.data['Date'])
        
        self.data = self.data.sort_values('Date').reset_index(drop=True)
    
    def _resample_data(self, timeframe: str) -> pd.DataFrame:
        """
        Resample data to specified timeframe.
        
        Args:
            timeframe: 'D' (day), 'W' (week), 'M' (month), 'Q' (quarter), 'Y' (year)
        
        Returns:
            Resampled DataFrame with OHLCV data
        """
        df = self.data.copy()
        df.set_index('Date', inplace=True)
        
        # Resample OHLC data
        resampled = pd.DataFrame()
        resampled['Open'] = df['Open'].resample(timeframe).first()
        resampled['High'] = df['High'].resample(timeframe).max()
        resampled['Low'] = df['Low'].resample(timeframe).min()
        resampled['Close'] = df['Close'].resample(timeframe).last()
        
        if 'Volume' in df.columns:
            resampled['Volume'] = df['Volume'].resample(timeframe).sum()
        
        resampled = resampled.dropna()
        resampled.reset_index(inplace=True)
        
        return resampled
    
    def plot_candlestick(self,
                        timeframe: str = 'D',
                        title: Optional[str] = None,
                        show_volume: bool = True,
                        moving_averages: Optional[List[int]] = None,
                        height: int = 800,
                        show_rangeslider: bool = True,
                        color_scheme: str = 'default') -> go.Figure:
        """
        Create an interactive candlestick chart.
        
        Args:
            timeframe: Timeframe for candlesticks
                      'D' or 'day' - Daily
                      'W' or 'week' - Weekly
                      'M' or 'month' - Monthly
                      'Q' or 'quarter' - Quarterly
                      'Y' or 'year' - Yearly
            title: Custom chart title
            show_volume: Whether to show volume bars
            moving_averages: List of periods for moving averages (e.g., [20, 50, 200])
            height: Chart height in pixels
            show_rangeslider: Whether to show range slider
            color_scheme: 'default' (green/red) or 'classic' (white/black)
        
        Returns:
            Plotly Figure object
        
        Example:
            >>> visualizer = CandlestickVisualizer(data, 'RELIANCE')
            >>> fig = visualizer.plot_candlestick(timeframe='W', moving_averages=[20, 50])
            >>> fig.show()
        """
        # Map timeframe aliases
        timeframe_map = {
            'day': 'D', 'daily': 'D', 'd': 'D',
            'week': 'W', 'weekly': 'W', 'w': 'W',
            'month': 'M', 'monthly': 'M', 'm': 'M',
            'quarter': 'Q', 'quarterly': 'Q', 'q': 'Q',
            'year': 'Y', 'yearly': 'Y', 'y': 'Y', 'a': 'Y'
        }
        
        tf = timeframe_map.get(timeframe.lower(), timeframe.upper())
        
        # Timeframe names for display
        timeframe_names = {
            'D': 'Daily',
            'W': 'Weekly',
            'M': 'Monthly',
            'Q': 'Quarterly',
            'Y': 'Yearly'
        }
        
        # Resample data if not daily
        if tf == 'D':
            plot_data = self.data.copy()
        else:
            plot_data = self._resample_data(tf)
        
        # Create subplots
        if show_volume and 'Volume' in plot_data.columns:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(f'{self.symbol} - {timeframe_names.get(tf, tf)} Chart', 'Volume')
            )
        else:
            fig = go.Figure()
        
        # Color scheme
        if color_scheme == 'classic':
            increasing_color = 'white'
            decreasing_color = 'black'
            increasing_line_color = 'black'
            decreasing_line_color = 'black'
        else:  # default
            increasing_color = '#26a69a'  # Green
            decreasing_color = '#ef5350'  # Red
            increasing_line_color = '#26a69a'
            decreasing_line_color = '#ef5350'
        
        # Add candlestick trace
        candlestick = go.Candlestick(
            x=plot_data['Date'],
            open=plot_data['Open'],
            high=plot_data['High'],
            low=plot_data['Low'],
            close=plot_data['Close'],
            name='OHLC',
            increasing=dict(
                line=dict(color=increasing_line_color),
                fillcolor=increasing_color
            ),
            decreasing=dict(
                line=dict(color=decreasing_line_color),
                fillcolor=decreasing_color
            )
        )
        
        if show_volume and 'Volume' in plot_data.columns:
            fig.add_trace(candlestick, row=1, col=1)
        else:
            fig.add_trace(candlestick)
        
        # Add moving averages
        if moving_averages:
            colors = ['#2962FF', '#FF6D00', '#00C853', '#AA00FF', '#FFD600']
            for i, period in enumerate(moving_averages):
                if len(plot_data) >= period:
                    ma = plot_data['Close'].rolling(window=period).mean()
                    ma_trace = go.Scatter(
                        x=plot_data['Date'],
                        y=ma,
                        mode='lines',
                        name=f'MA{period}',
                        line=dict(color=colors[i % len(colors)], width=1.5),
                        opacity=0.7
                    )
                    if show_volume and 'Volume' in plot_data.columns:
                        fig.add_trace(ma_trace, row=1, col=1)
                    else:
                        fig.add_trace(ma_trace)
        
        # Add volume bars
        if show_volume and 'Volume' in plot_data.columns:
            # Color volume bars based on price movement
            colors_volume = [
                increasing_color if plot_data['Close'].iloc[i] >= plot_data['Open'].iloc[i]
                else decreasing_color
                for i in range(len(plot_data))
            ]
            
            volume_trace = go.Bar(
                x=plot_data['Date'],
                y=plot_data['Volume'],
                name='Volume',
                marker=dict(color=colors_volume),
                showlegend=False
            )
            fig.add_trace(volume_trace, row=2, col=1)
        
        # Update layout
        if title is None:
            title = f'{self.symbol} - {timeframe_names.get(tf, tf)} Candlestick Chart'
        
        layout_updates = dict(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center',
                font=dict(size=20)
            ),
            xaxis=dict(
                rangeslider=dict(visible=show_rangeslider) if not show_volume else dict(visible=False),
                type='date',
                title='Date'
            ),
            yaxis=dict(
                title='Price',
                side='right'
            ),
            hovermode='x unified',
            height=height,
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        if show_volume and 'Volume' in plot_data.columns:
            layout_updates['xaxis2'] = dict(title='Date')
            layout_updates['yaxis2'] = dict(title='Volume', side='right')
        
        fig.update_layout(**layout_updates)
        
        return fig
    
    def plot_daily(self, **kwargs) -> go.Figure:
        """Create daily candlestick chart."""
        return self.plot_candlestick(timeframe='D', **kwargs)
    
    def plot_weekly(self, **kwargs) -> go.Figure:
        """Create weekly candlestick chart."""
        return self.plot_candlestick(timeframe='W', **kwargs)
    
    def plot_monthly(self, **kwargs) -> go.Figure:
        """Create monthly candlestick chart."""
        return self.plot_candlestick(timeframe='M', **kwargs)
    
    def plot_quarterly(self, **kwargs) -> go.Figure:
        """Create quarterly candlestick chart."""
        return self.plot_candlestick(timeframe='Q', **kwargs)
    
    def plot_yearly(self, **kwargs) -> go.Figure:
        """Create yearly candlestick chart."""
        return self.plot_candlestick(timeframe='Y', **kwargs)
    
    def save_chart(self, 
                   fig: go.Figure,
                   filename: str,
                   format: str = 'html',
                   width: Optional[int] = None,
                   height: Optional[int] = None):
        """
        Save chart to file.
        
        Args:
            fig: Plotly figure to save
            filename: Output filename
            format: 'html', 'png', 'jpg', 'svg', 'pdf'
            width: Image width (for static formats)
            height: Image height (for static formats)
        
        Example:
            >>> fig = visualizer.plot_weekly()
            >>> visualizer.save_chart(fig, 'weekly_chart.html')
            >>> visualizer.save_chart(fig, 'weekly_chart.png', format='png', width=1920, height=1080)
        """
        if format.lower() == 'html':
            fig.write_html(filename)
        else:
            fig.write_image(filename, format=format, width=width, height=height)
        
        print(f"Chart saved to: {filename}")
    
    def create_comparison_chart(self,
                               timeframes: List[str] = ['D', 'W', 'M'],
                               moving_averages: Optional[List[int]] = None,
                               height: int = 1200) -> go.Figure:
        """
        Create a comparison chart with multiple timeframes.
        
        Args:
            timeframes: List of timeframes to display
            moving_averages: Moving averages to overlay
            height: Total chart height
        
        Returns:
            Plotly Figure with subplots for each timeframe
        
        Example:
            >>> fig = visualizer.create_comparison_chart(['D', 'W', 'M'])
            >>> fig.show()
        """
        n_charts = len(timeframes)
        
        timeframe_names = {
            'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly',
            'Q': 'Quarterly', 'Y': 'Yearly'
        }
        
        subplot_titles = [f'{timeframe_names.get(tf, tf)}' for tf in timeframes]
        
        fig = make_subplots(
            rows=n_charts, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.05,
            subplot_titles=subplot_titles,
            row_heights=[1/n_charts] * n_charts
        )
        
        colors = ['#26a69a', '#ef5350']
        ma_colors = ['#2962FF', '#FF6D00', '#00C853']
        
        for i, tf in enumerate(timeframes, 1):
            # Resample data
            if tf == 'D':
                plot_data = self.data.copy()
            else:
                plot_data = self._resample_data(tf)
            
            # Add candlestick
            candlestick = go.Candlestick(
                x=plot_data['Date'],
                open=plot_data['Open'],
                high=plot_data['High'],
                low=plot_data['Low'],
                close=plot_data['Close'],
                name=f'{timeframe_names.get(tf, tf)} OHLC',
                increasing_line_color=colors[0],
                decreasing_line_color=colors[1],
                showlegend=(i == 1)
            )
            fig.add_trace(candlestick, row=i, col=1)
            
            # Add moving averages
            if moving_averages:
                for j, period in enumerate(moving_averages):
                    if len(plot_data) >= period:
                        ma = plot_data['Close'].rolling(window=period).mean()
                        ma_trace = go.Scatter(
                            x=plot_data['Date'],
                            y=ma,
                            mode='lines',
                            name=f'MA{period}',
                            line=dict(color=ma_colors[j % len(ma_colors)], width=1),
                            showlegend=(i == 1)
                        )
                        fig.add_trace(ma_trace, row=i, col=1)
        
        fig.update_layout(
            title=dict(
                text=f'{self.symbol} - Multi-Timeframe Analysis',
                x=0.5,
                xanchor='center',
                font=dict(size=20)
            ),
            height=height,
            template='plotly_white',
            hovermode='x unified',
            showlegend=True
        )
        
        # Update y-axes
        for i in range(1, n_charts + 1):
            fig.update_yaxes(title_text='Price', row=i, col=1, side='right')
            fig.update_xaxes(title_text='Date', row=i, col=1)
        
        return fig
    
    def __repr__(self):
        return f"CandlestickVisualizer(symbol='{self.symbol}', records={len(self.data)})"
