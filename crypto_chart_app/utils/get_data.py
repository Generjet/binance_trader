import pandas as pd
from binance.client import Client
import os

def fetchCryptoData(symbol, timePeriod, lookback, ago='days ago UTC'):
    # Initialize Binance client (use your API keys if you have them)
    client = Client()    
    # Get historical klines/candlestick data
    klines = client.get_historical_klines(
        symbol=symbol,
        interval=timePeriod,
        limit=lookback
    )    
    # Create DataFrame
    df = pd.DataFrame(klines, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'Number_of_trades',
        'Taker_buy_base', 'Taker_buy_quote', 'Ignore'
    ])    
    # Convert string values to float
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    # Convert timestamp to datetime
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    return df