# Import packages
from dash import Dash, html, dash_table, dcc
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from binance.client import Client
import ta
import os
import sys

# GENERJET BINANCE ==>
# GENERJET API KEY and SECRET
api_key = os.getenv('binance_key')
api_secret = os.getenv('binance_secret')
client = Client(api_key, api_secret)
# ======== setting overall signal values to variables ====
currency = 'ETHUSDT'

# fetch new data
# ====== get data function ======
def fetchCryptoData(symbol, timePeriod ,lookback, ago='days ago UTC'):
    df = pd.DataFrame(client.get_historical_klines(symbol, timePeriod, lookback + ago ))
    df = df.iloc[:,:6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    # df['Time'] = pd.to_datetime(df['Time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M')
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index('Time', inplace=True)
    # df['Time'] = pd.to_datetime(df['Time'], unit='s').dt.strftime('%Y-%m-%d %H:%M')
    # df = df.astype(float)
    print(df.tail(10))
    return df

# Incorporate DATABASE
# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# sqlite-aas data unshina
# DB_NAME = '../tamir_crypto_data.db'
# conn = sqlite3.connect(DB_NAME)
# query = "SELECT * FROM crypto_data ORDER BY time DESC LIMIT 100"
# df = pd.read_sql_query(query, conn)
# conn.close()

# get new data
symbol = 'ETHUSDT'
timePeriod = '5m'
lookback = '60'
df = fetchCryptoData(symbol, timePeriod, lookback )

# Initialize the app
app = Dash()

# fig chart
fig = go.Figure(data=[
    go.Candlestick(
        x=df['Time'],
        open=df['Open'],
        high=df['High'],
        close=df['Close'],
        low=df['Low']
        )]
    )


# App layout
app.layout = [
    html.Div(children='Крипто арилжааны автомат бот 自動化'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.Graph(figure=fig),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
]

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
