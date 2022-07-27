from curses import window
from binance.spot import Spot
import os
from matplotlib.pyplot import get
import ta
import pandas as pd
from datetime import timedelta
import time

#  === 2 ==== create connection 
client = Spot()
# GENERJET API KEY and SECRET
API_KEY = os.getenv('api_key')
API_SECRET = os.getenv('api_secret')
print("API_KEY=",API_KEY)
print("API_SECRET=", API_SECRET)

# #Get server timestamp
# print(client.time())
# # Get klines of BTCUSDT at 1m interval
# print(client.klines("BTCUSDT", "1m"))
# # Get last 10 klines of BNBUSDT at 1h interval
# print(client.klines("BNBUSDT", "1h", limit=10))

# api key/secret are required for user data endpoints
client = Spot(key=API_KEY, secret=API_SECRET)

# Get account and balance information
print(client.account())


#  === 2 ==== get data
symbol = "ETHUSDT"

def getData(symbol):
    frame = pd.DataFrame(client.klines(symbol, '15m'))
    frame = frame.iloc[:,0:5]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close']
    frame.set_index('Time', inplace=True)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

df = getData(symbol)
print(df)

# === 3 === technical indicator
def indicators(df):
    df['SMA_200'] = ta.trend.sma_indicator(df.Close, window=200)
    df['stochrsi_k'] = ta.momentum.stochrsi_k(df.Close, window=10)
    df.dropna(inplace=True)
    df['Buy'] = (df.Close > df.SMA_200) & (df.stochrsi_k < 0.05)
    return df

indicated_data = indicators(df)
print(indicated_data)

# === continue ===> 
# ==== https://www.youtube.com/watch?v=VZQg4KSmpQU&list=TLPQMjYwNzIwMjKJH6nEbJ9pcw&index=3 