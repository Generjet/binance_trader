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
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    # print(df.tail(10))
    return df

# sqlite-aas data unshina
# DB_NAME = '../tamir_crypto_data.db'
# conn = sqlite3.connect(DB_NAME)

# # Create table if it doesn't exist
# create_table_query = """
# CREATE TABLE IF NOT EXISTS crypto_data (
#     Time DATETIME PRIMARY KEY,
#     Open REAL,
#     High REAL,
#     Low REAL,
#     Close REAL,
#     Volume REAL
# );
# """
# conn.execute(create_table_query)
# conn.commit()

# # Try to read existing data
# try:
#     query = "SELECT * FROM crypto_data ORDER BY Time DESC LIMIT 100"
#     df = pd.read_sql_query(query, conn)
# except pd.errors.DatabaseError:
#     # If table is empty or error occurs, create empty DataFrame
#     df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

# conn.close()

# get new data
symbol = 'ETHUSDT'
timePeriod = '4h'
lookback = '200'
df = fetchCryptoData(symbol, timePeriod, lookback )

# =========== extremum ===============
def find_extremum(df):
    # Ensure 'High' column is numeric
    # df['High'] = pd.to_numeric(df['High'])

    # Find the last 2 maximum points of 'High'
    max_points = df['High'].nlargest(2)
    if len(max_points) < 2:
        df['resistance'] = None
        return df

    # Calculate the slope
    slope = (max_points.iloc[1] - max_points.iloc[0]) / (max_points.index[1] - max_points.index[0]).days

    # Calculate the next values for 'Resistance'
    df['resistance'] = max_points.iloc[1] + slope * (df.index - max_points.index[1]).days
    print("extremums = ", df.tail(10))
    return df

 # =========== TA technical analysis ===============
def applytechnicals(df):
    # Ensure columns are numeric
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    # Calculate technical indicators
    df['%K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
    df['macd'] = ta.trend.macd_diff(df['Close'])
    df['ema'] = df['Close'].ewm(span=14, adjust=False).mean()
    # Drop any rows with NaN values
    df.dropna(inplace=True)
    print("technicals => ",df.tail(10))
    return df
# Initialize the app ============ VIZUALIZE ============
app = Dash()
df = find_extremum(df)
df = applytechnicals(df)
print(df.tail(10))

# Convert columns to numeric
df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].apply(pd.to_numeric)

# Create candlestick chart
fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
)])

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
