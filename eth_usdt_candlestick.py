import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# Function to fetch historical data
def fetch_historical_data(symbol, interval, limit):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", 
        "close_time", "quote_asset_volume", "number_of_trades", 
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]]
    df = df.astype(float)
    return df

# Streamlit app
st.title("ETH/USDT Candlestick Chart")

# Fetch data
symbol = "ETHUSDT"
interval = "1h"
limit = 100
data = fetch_historical_data(symbol, interval, limit)

# Display candlestick chart
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data["open"],
    high=data["high"],
    low=data["low"],
    close=data["close"]
)])

st.plotly_chart(fig)
