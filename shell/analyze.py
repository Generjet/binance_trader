import yfinance as yf
import mplfinance as mpf
from binance.client import Client
import os
import ta
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import polars as pl
import datetime
import csv

# GENERJET API KEY and SECRET
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

client = Client(api_key, api_secret)

# ====== get data function ======
def fetchCryptoData(symbol, timePeriod ,lookback, ago='days ago UTC'):
    frame = pd.DataFrame(client.get_historical_klines(symbol, timePeriod, lookback + ago ))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame.set_index('Time', inplace=True)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

# print("Hour4", hour4)
# return signal to shell
print("wait")

# === SLOPE, INTERCEPTS and difference STEPS ====
# 2 argument l avna
def direction_and_steps(datapoints, df):
    if datapoints.index[0] > datapoints.index[1]:
        startIndex = datapoints.index[0]
        endIndex = datapoints.index[1]
    else:
        startIndex = datapoints.index[1]
        endIndex = datapoints.index[0]
    a = datapoints.head(1)
    b = datapoints.tail(1)
    a_value = a[0]
    b_value = b[0]
    ascending = False

# ========================
    if b.index < a.index:
        oldIndex = b.index
        newIndex = a.index
        if b_value > a_value:
            max = b_value
            min = a_value
            ascending = False
            print("descending")
        else:
            max = a_value
            min = b_value
            ascending = True
            print('ascending')
    elif b.index > a.index:
        oldIndex = a.index
        newIndex = b.index
        if b_value > a_value:
            max = b_value
            min = a_value
            ascending = True
            print('ascending')
        else:
            max = a_value
            min = b_value
            ascending = False
            print('descending')

    top_diff = max - min
    # print('difference = ', top_diff)
    filtered = df[(df.index <= startIndex) & (df.index >= endIndex)]
    numrange = len(filtered)
    # print('range =', numrange)
    diff_step = top_diff/numrange
    return diff_step, ascending
# === test ===
# resistance_points = resistances.sort_values(ascending=False).tail(2)

# diff_step, lineAscending = direction_and_steps(resistance_points)
# # print('diff = ', diff_step)
# lineAscending

# ==== RETURN min & max from 2 POINTS ====
def min_max(datapoints):
    a = datapoints.head(1)
    b = datapoints.tail(1)
    a_value = a[0]
    b_value = b[0]
    if b_value > a_value:
        max = b_value
        min = a_value
        print("max= ", max, "min= ", min)
    else:
        max = a_value
        min = b_value
        print("max= ", max, "min= ", min)
    return min, max

# ===== EXTREMUM hoorondiin data range easify =====
def start_end_ragne(datapoints):
    if datapoints.index[1] > datapoints.index[0]:
        startIndex = datapoints.index[0]
        endIndex = datapoints.index[1]
    else:
        startIndex = datapoints.index[1]
        endIndex = datapoints.index[0]
    return startIndex, endIndex

# === RESISTANCE until NOW ===
def resistance(df):
    # print("Calculating resistance")
    resistances = df[df.High == df.High.rolling(10, center=True).max()].High
    resistance_points = resistances.sort_values(ascending=True).tail(2)

    # resistance coefficients
    diff_step, lineAscending = direction_and_steps(resistance_points, df)
    start, end = start_end_ragne(resistance_points)
    # today = df[(df.index > resistance_points.index[0])]
    today = df[(df.index > start)]

    x_values = []
    y_values = []

    min, max = min_max(resistance_points)
    y = resistance_points[0]
    # today['resistance'] = np.nan

    if lineAscending == True:
        y = min
        for i in today.index:
            y = y + diff_step
            y_values.append(y)
            x_values.append(i)
            # today.loc[today.index==i, 'resistance'] = y
            df.loc[df.index==i, 'resistance'] = y
    elif lineAscending == False:
        y = max
        for i in today.index:
            y = y - diff_step
            y_values.append(y)
            x_values.append(i)
            # today.loc[today.index==i, 'resistance'] = y
            df.loc[df.index==i, 'resistance'] = y

    print("Resistance ascending", lineAscending)
    # print("Diff points", diff_step)
    # # y_values
# ==== run test ====
# resistance(df)

# ======== SUPPORT =======
def support(df):
    supports = df[df.Low == df.Low.rolling(10, center=True).min()].Low
    support_points = supports.sort_values(ascending=True).head(2)
    
    # start_point
    start, end = start_end_ragne(support_points)
    support_today = df[(df.index > start)]
    # support coefficients
    diff_step, lineAscending = direction_and_steps(support_points, df)

    numrange = len(support_today)
    x_values = []
    y_values = []

    min, max = min_max(support_points)
    y = support_points[0]
    if lineAscending == True:
        y = min
        for i in support_today.index:
            nth_row = df.loc[df.index == i]
            print('NTH row ==> ', nth_row)
            
            if (nth_row.resistance != np.nan) & (nth_row.support != np.nan) & (nth_row.resistance <= nth_row.support):
                print('Crossed')
                y = nth_row.Low - 20
            else:
                y = y + diff_step
            y_values.append(y)
            x_values.append(i)
            df.loc[df.index==i, 'support'] = y
    elif lineAscending == False:
        y = max
        for i in support_today.index:
            y = y - diff_step
            y_values.append(y)
            x_values.append(i)
            df.loc[df.index==i, 'support'] = y

# ===== PLOT and SAVE ======
# ====== PLOTTING and SAVING =========
def plot_df(df):
# ==== SUBPLOTS =====
    fig,axes = plt.subplots(nrows=4,ncols=1,figsize=(12,9))
    axes[0].plot(df['High'], label="High")
    axes[0].plot(df['Low'], label='Low')
    axes[0].set_title("ETHUSDT Price movement")
    axes[0].plot(df['resistance'], 'r', label="resistance")
    axes[0].plot(df['support'], 'g', label="support")
    axes[0].plot(df['sell_zone'], 'r--', label="sell_zone")
    axes[0].plot(df['buy_zone'], 'g--', label="buy_zone")
    axes[0].plot(df.index, df['Buy'], 'ro')
    axes[0].plot(df.index, df['Sell'], 'go')
    axes[0].plot(df.index, df['ema'], 'b--')
    # axes[0].plot(levels.index, levels, 'b')
    axes[1].plot(df["%D"], 'r', label="%D")
    axes[1].plot(df["%K"], 'b', label="%K")
    axes[1].set_title("STOCHASTIC OSCILLATOR")
    axes[1].axhline(y=80,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    axes[1].axhline(y=20,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    axes[2].plot(df["rsi"], 'r', label="RSI")
    axes[2].set_title("RSI")
    axes[2].axhline(y=70,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    axes[2].axhline(y=30,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    axes[3].plot(df["macd"], 'r', label="MACD")
    axes[3].set_title("MACD")
    axes[3].axhline(y=0,xmin=0,xmax=3,c="blue",linewidth=1.5,zorder=0)
    axes[3].axhline(y=5,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    axes[3].axhline(y=-5,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    fig.tight_layout()
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    startDate = df.index[0].strftime("%Y-%m-%d")
    endDate = df.index[-1].strftime("%Y-%m-%d")
    save_name = startDate + '_to_' + endDate
    save_name
    plt.savefig('graphs/4h_test_' +save_name+'_signals.jpg')

# ===== MACD & RSI & STOCHASTIC OSCILLATOR =======
def applytechnicals(df):
    # window for 14 days and smooth window for 3days
    df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=14)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df['ema'] = df.iloc[:,0].ewm(span=14,adjust=False).mean()
    df.dropna(inplace=True)
    return df

# ==== LONG and SHORT decide =====
def long_short_decide(long, short):
    long['buy_zone'] = long['support'] + 120
    long['sell_zone'] = long['resistance'] - 120
    short['buy_zone'] = short['support'] + 60
    short['sell_zone'] = short['resistance'] - 60
    # ==== BUY, if it is within channel and not yet overbought ====
    current = short.tail(1)
    longTerm = long.tail(1)
    # === SHORT check ====
    short['Buy'] = np.where( (short['Close'] > short['ema']) & (short['rsi'] < 30) & ( short['Low'] < short['buy_zone'] ) & ( short['support'] < short['resistance'] ) , short['Close'], np.nan )
    short['Sell'] = np.where( (short['Close'] < short['ema']) & (short['rsi'] > 50) & ( short['High'] > short['sell_zone'] ) & ( short['support'] < short['resistance'] )  , short['Close'], np.nan )
    # === LONG check ====
    long['Buy'] = np.where( (long['Close'] > long['ema']) & (long['rsi'] < 50) & ( long['Low'] < long['buy_zone'] ) , long['Close'], np.nan )
    # long['Sell'] = np.where( (long['rsi'] > 50) & ( long['High'] > long['sell_zone'] ) & ( long['support'] < long['resistance'] ) & (long['%K'].between(60,100)) & (long['%D'].between(60,100)) & (long['%K'] > long['%D'] ) , long['Close'], np.nan )
    long['Sell'] = np.where( (long['Close'] < long['ema']) & (long['rsi'] > 40) & ( long['Close'] > long['sell_zone'] ) & ( long['support'] < long['resistance'] ) , long['Close'], np.nan )

    # === LONGTERM ==> Buy, if price goes UP and breaks RESISTANCE or SELL if breaks SUPPORT ===
    signal = 'wait'
    if (current['Close'][0] > longTerm['resistance'][0]) & (longTerm['rsi'][0] > 70 ):
        breakout_buy = True
        print("BREAKOUT BUY TRUE")
        signal = 'buy'
    elif (current['Close'][0] < longTerm['support'][0]) & (longTerm['rsi'][0] < 30 ):
        print("BREAKOUT SELL TRUE")
        breakout_buy = False
        signal = 'sell'
    elif (current['Close'][0] > longTerm['sell_zone'][0]) & (current['Close'][0] < longTerm['resistance'][0]) & (longTerm['rsi'][0] > 60):
        print("CHANNEL SELL")
        signal = 'sell'
    elif (current['Close'][0] < longTerm['buy_zone'][0]) & (current['Close'][0] > longTerm['support'][0]) & (longTerm['rsi'][0] < 30):
        print("CHANNEL BUY")
        signal = 'buy'
    # return long, short
    return signal

# SHORT TERM data
symbol = 'ETHUSDT'
timePeriod = '30m'
lookback = '60'
min30 = fetchCryptoData(symbol, timePeriod, lookback )
min30['resistance'] = np.nan
min30['support'] = np.nan
min30['macd'] = np.nan
min30['rsi'] = np.nan
min30['%D'] = np.nan
min30['%K'] = np.nan

#LOGN TERM data
symbol = 'ETHUSDT'
timePeriod = '4h'
lookback = '96'
hour4 = fetchCryptoData(symbol, timePeriod, lookback )
hour4['resistance'] = np.nan
hour4['support'] = np.nan
hour4['macd'] = np.nan
hour4['rsi'] = np.nan
hour4['%D'] = np.nan
hour4['%K'] = np.nan

# ===== PERFORM ======
resistance(hour4)
support(hour4)
resistance(min30)
support(min30)
applytechnicals(hour4)
applytechnicals(min30)
signal = long_short_decide(hour4, min30)
plot_df(hour4)
print("SIGNAL =====> ", signal)


# ==================================================
# # ===== UPDATE ROW if "Sell" is confirmed ========
# def update_csv_data(sell_date, sell_amount, sell_price):
#     # Specify the path to your CSV file
#     csv_file_path = "orders.csv"

#     # Read data from CSV file and update rows if status matches "wait"
#     updated_rows = []
#     with open(csv_file_path, 'r', newline='') as file:
#         reader = csv.DictReader(file)
#         fieldnames = reader.fieldnames

#         for row in reader:
#             if row['sell_date'] == 'wait':
#                 row['sell_amount'] = str(sell_amount)
#                 row['sell_price'] = str(sell_price)
#                 row['sell_date'] = '2023-07-28 06:30:00'
#             updated_rows.append(row)

#     # Write the updated data back to the CSV file, overwriting the existing contents
#     with open(csv_file_path, 'w', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(updated_rows)

# # Example usage:
# sell_date = "wait"
# sell_amount = 0.66
# sell_price = 2025.99
# update_csv_data(sell_date, sell_amount, sell_price)