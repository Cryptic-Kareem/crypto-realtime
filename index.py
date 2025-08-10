import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from threading import Thread

# Initialize the Dash app with dark theme
app = dash.Dash(__name__)

# Set dark theme for the app
app.layout = html.Div(
    style={
        'backgroundColor': '#111111',
        'color': '#111111',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif',
    },
    children=[
        # Header
        html.H1("Cryptocurrency Dashboard", style={'color': 'white'}),
        
        # Dropdown for coin selection
        html.Div([
            html.Label("Select Cryptocurrency:", style={'color': 'white'}),
            dcc.Dropdown(
                id='coin-dropdown',
                options=[
                    {'label': 'Bitcoin (BTC)', 'value': 'bitcoin'},
                    {'label': 'Ethereum (ETH)', 'value': 'ethereum'},
                    {'label': 'XRP (XRP)', 'value': 'ripple'},
                    {'label': 'Cardano (ADA)', 'value': 'cardano'},
                    {'label': 'Solana (SOL)', 'value': 'solana'},
                ],
                value='bitcoin',
                style={
                    'backgroundColor': '#222222',
                    'color': 'black',
                }
            ),
        ]),
        
        # Chart
        dcc.Graph(id='crypto-chart'),
        
        # Interval component for automatic updates - now 5 seconds
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # in milliseconds (5 seconds)
            n_intervals=0
        )
    ]
)

# Initial price points for different coins
COIN_BASE_PRICES = {
    'bitcoin': 30000,
    'ethereum': 2000,
    'ripple': 0.5,
    'cardano': 0.4,
    'solana': 100,
}

# Store the generated data
generated_data = {}

def generate_ohlc_data(coin_id, days=7):
    """Generate random OHLC data for a cryptocurrency"""
    base_price = COIN_BASE_PRICES.get(coin_id, 100)
    
    # Create date range for the past 7 days with hourly data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='h')
    
    # Generate random price movements
    np.random.seed(int(time.time()) % 100)  # Change seed for randomness but keep some consistency
    
    # Create price trend with some randomness
    price_trend = np.cumsum(np.random.normal(0, base_price * 0.01, len(date_range)))
    
    # Generate OHLC data
    data = []
    for i, date in enumerate(date_range):
        trend_value = price_trend[i]
        open_price = base_price + trend_value
        high_price = open_price * (1 + np.random.uniform(0, 0.02))
        low_price = open_price * (1 - np.random.uniform(0, 0.02))
        close_price = np.random.uniform(low_price, high_price)
        volume = np.random.uniform(base_price * 1000, base_price * 5000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(data)

# Function to update data periodically - now every 5 seconds
def update_data_periodically():
    while True:
        for coin_id in COIN_BASE_PRICES.keys():
            generated_data[coin_id] = generate_ohlc_data(coin_id)
        time.sleep(5)  # Update every 5 seconds

# Start the background thread for data updates
data_thread = Thread(target=update_data_periodically, daemon=True)
data_thread.start()

# Initialize data for all coins
for coin_id in COIN_BASE_PRICES.keys():
    generated_data[coin_id] = generate_ohlc_data(coin_id)

# Callback to update the chart
@app.callback(
    Output('crypto-chart', 'figure'),
    [Input('coin-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_chart(selected_coin, n_intervals):
    # Get data for the selected coin
    df = generated_data.get(selected_coin, pd.DataFrame())
    
    if df.empty:
        return go.Figure()
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="OHLC"
        )
    )
    
    # Add line chart for closing prices
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['close'],
            mode='lines',
            name='Close Price',
            line=dict(color='purple', width=1)
        )
    )
    
    # Add volume as bar chart on secondary y-axis
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            name='Volume',
            opacity=0.3
        ),
        secondary_y=True
    )
    
    # Set figure layout with dark theme
    coin_names = {
        'bitcoin': 'Bitcoin (BTC)',
        'ethereum': 'Ethereum (ETH)',
        'ripple': 'XRP (XRP)',
        'cardano': 'Cardano (ADA)',
        'solana': 'Solana (SOL)',
    }
    
    fig.update_layout(
        title=f"{coin_names.get(selected_coin, selected_coin)} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        yaxis2_title="Volume",
        height=600,
        template="plotly_dark",  # Use dark template
        paper_bgcolor='#222222',
        plot_bgcolor='#222222',
        font=dict(color='white')
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)