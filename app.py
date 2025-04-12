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
server = app.server  # Required for production servers like gunicorn

# Set dark theme for the app
app.layout = html.Div(
    style={
        'backgroundColor': '#111111',
        'color': '#111111',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif',
    },
    children=[
        html.H1("Cryptocurrency Dashboard", style={'color': 'white'}),
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
                style={'backgroundColor': '#222222', 'color': 'black'}
            ),
        ]),
        dcc.Graph(id='crypto-chart'),
        dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)
    ]
)

COIN_BASE_PRICES = {
    'bitcoin': 30000,
    'ethereum': 2000,
    'ripple': 0.5,
    'cardano': 0.4,
    'solana': 100,
}

generated_data = {}

def generate_ohlc_data(coin_id, days=7):
    base_price = COIN_BASE_PRICES.get(coin_id, 100)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='h')  # ✅ 'h' instead of 'H'

    np.random.seed(int(time.time()) % 100)
    price_trend = np.cumsum(np.random.normal(0, base_price * 0.01, len(date_range)))

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

def update_data_periodically():
    while True:
        for coin_id in COIN_BASE_PRICES.keys():
            generated_data[coin_id] = generate_ohlc_data(coin_id)
        time.sleep(5)

data_thread = Thread(target=update_data_periodically, daemon=True)
data_thread.start()

for coin_id in COIN_BASE_PRICES.keys():
    generated_data[coin_id] = generate_ohlc_data(coin_id)

@app.callback(
    Output('crypto-chart', 'figure'),
    [Input('coin-dropdown', 'value'), Input('interval-component', 'n_intervals')]
)
def update_chart(selected_coin, n_intervals):
    df = generated_data.get(selected_coin, pd.DataFrame())
    if df.empty:
        return go.Figure()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Candlestick(
        x=df['timestamp'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name="OHLC"
    ))

    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['close'], mode='lines',
        name='Close Price', line=dict(color='purple', width=1)
    ))

    fig.add_trace(go.Bar(
        x=df['timestamp'], y=df['volume'], name='Volume', opacity=0.3
    ), secondary_y=True)

    coin_names = {
        'bitcoin': 'Bitcoin (BTC)',
        'ethereum': 'Ethereum (ETH)',
        'ripple': 'XRP (XRP)',
        'cardano': 'Cardano (ADA)',
        'solana': 'Solana (SOL)',
    }

    fig.update_layout(
        title=f"{coin_names.get(selected_coin, selected_coin)} Price Chart",
        xaxis_title="Date", yaxis_title="Price (USD)", yaxis2_title="Volume",
        height=600, template="plotly_dark", paper_bgcolor='#222222',
        plot_bgcolor='#222222', font=dict(color='white')
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)  # ✅ Fixed method name
