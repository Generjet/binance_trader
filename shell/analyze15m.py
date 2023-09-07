from binance.client import Client
import os
import ta
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import csv
import sqlite3
from os.path import exists as file_exists
import sys

# period parameters are: 1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M
# period = sys.argv[1]
period = '15m'
#print("period parameters are: 1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M")
print ("=== PYTHON ==============> The GIVEN PERIOD is: " + period)

# sys.exit(0)

# GENERJET API KEY and SECRET
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
client = Client(api_key, api_secret)
# ======== setting overall signal values to variables ====
currency = 'ETHUSDT'

# ====== get data function ======
def fetchCryptoData(symbol, timePeriod ,lookback, ago='days ago UTC'):
    frame = pd.DataFrame(client.get_historical_klines(symbol, timePeriod, lookback + ago ))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame.set_index('Time', inplace=True)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

#print("wait")

# === RESISTANCE until NOW ===
def resistance(df):
    # print("Calculating resistance")
    resistances = df[df.High == df.High.rolling(10, center=True).max()].High
    resistance_points = resistances.sort_values(ascending=True).tail(2)
    resistance_mean = resistance_points.max()
    
    #print("RESISTANCES ", resistances)
    #print("RESISTANCES MEAN P0INT ", resistance_mean)
    df['resistance'] = resistance_mean

# ======== SUPPORT =======
def support(df):
    supports = df[df.Low == df.Low.rolling(10, center=True).min()].Low
    support_points = supports.sort_values(ascending=True).head(2)
    support_mean = supports.min()
    #print("SUPPORTS ", supports)
    #print("SUPPORTS MEAN PINT ", support_mean)
    df['support'] = support_mean

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
    plt.savefig('graphs/CLEAN_SIMPLE_4h_test_' +save_name+'_signals.jpg')

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
    long['buy_zone'] = long['support'] + long['support']* 0.095 # === Хамгийн чухал нь support&resistance-аас хэдэн хувь зайтай buy&sell zone байх нь чухал нөлөөтэй!!!
    long['sell_zone'] = long['resistance'] - long['resistance'] * 0.07
    short['buy_zone'] = short['support'] + short['support'] * 0.095
    short['sell_zone'] = short['resistance'] - short['resistance'] * 0.07
    # ==== BUY, if is within channel and not yet overbought ====
    current = short.tail(1)
    longTerm = long.tail(1)
    #print('CURRENT value ',current)
    #print('LONGMAA ', longTerm)
    # === SHORT check ====
    short['Buy'] = np.where( (short['Close'] > short['ema']) & (short['rsi'] < 45) & ( short['Low'] < short['buy_zone'] ) & ( short['support'] < short['resistance'] ) , short['Close'], np.nan )
    short['Sell'] = np.where( (short['Close'] < short['ema']) & (short['rsi'] > 50) & ( short['High'] > short['sell_zone'] ) & ( short['support'] < short['resistance'] )  , short['Close'], np.nan )
    # === LONG check ====
    long['Buy'] = np.where( (long['%K'].between(0,30)) & (long['%D'].between(0,30)) & (long['%K'] < long['%D'] ) & (long['rsi'] < 50) & ( long['Low'] < long['buy_zone'] ) , long['Close'], np.nan )
    long['Sell'] = np.where( (long['%K'].between(75,100)) & (long['%D'].between(75,100)) & (long['%K'] > long['%D'] ) & (long['rsi'] > 65) & ( long['Close'] > long['sell_zone'] ) & ( long['support'] < long['resistance'] ) , long['Close'], np.nan )

    # === Buy, if price goes UP and breaks RESISTANCE or SELL if breaks SUPPORT ===
    signal = 'wait'
    if (current['Close'][0] > longTerm['resistance'][0]) & (longTerm['rsi'][0] > 70 ):
        breakout_buy = True
        #print("BREAKOUT BUY TRUE")
        signal = 'buy'
    elif (current['Close'][0] < longTerm['support'][0]) & (longTerm['rsi'][0] < 30 ):
        #print("BREAKOUT SELL TRUE")
        breakout_buy = False
        signal = 'sell'
    elif (current['Close'][0] > longTerm['sell_zone'][0]) & (current['Close'][0] < longTerm['resistance'][0]) & (longTerm['rsi'][0] > 60):
        #print("CHANNEL SELL")
        signal = 'sell'
    elif (current['Close'][0] < longTerm['buy_zone'][0]) & (current['Close'][0] > longTerm['support'][0]) & (longTerm['rsi'][0] < 30):
        #print("CHANNEL BUY")
        signal = 'buy'
    return signal
# =======================================================

# SHORT TERM data
symbol = 'ETHUSDT'
timePeriod = '5m'
lookback = '60'
shortTerm = fetchCryptoData(symbol, timePeriod, lookback )
shortTerm['resistance'] = np.nan
shortTerm['support'] = np.nan
shortTerm['macd'] = np.nan
shortTerm['rsi'] = np.nan
shortTerm['%D'] = np.nan
shortTerm['%K'] = np.nan

#LOGN TERM data
symbol = 'ETHUSDT'
timePeriod = period
lookback = '96'
longTerm = fetchCryptoData(symbol, timePeriod, lookback )
longTerm['resistance'] = np.nan
longTerm['support'] = np.nan
longTerm['macd'] = np.nan
longTerm['rsi'] = np.nan
longTerm['%D'] = np.nan
longTerm['%K'] = np.nan

#print("DATA fetched for"+period, longTerm)
# ===== PERFORM ======
resistance(longTerm)
support(longTerm)
resistance(shortTerm)
support(shortTerm)
applytechnicals(longTerm)
applytechnicals(shortTerm)
signal = long_short_decide(longTerm, shortTerm)
plot_df(longTerm)
print("SIGNAL =====> ", signal)


# ==================================================
# ===== INSERT INTO SIGNALS.CSV =========
now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
fileName = 'trade_signals.csv'

# === PREPARE signals ROW ====
newest = longTerm.tail(1)
# ======== setting overall signal values to variables ====
last_close_price = shortTerm.tail(1)['Close'][0]
rsi = newest['rsi'][0]
k = newest['%K'][0]
d = newest['%D'][0]
macd = newest['macd'][0]
support = newest['support'][0]
resistance = newest['resistance'][0]
buy_zone = newest['buy_zone'][0]
sell_zone = newest['sell_zone'][0]
bot_signal = signal
print('BUY_ZONE ', buy_zone)

header = ['date','rsi','%K','%D','macd','support','resistance','buy_zone','sell_zone','period']
signalValues  = []
signalValues.insert(0,now)
signalValues.insert(1, newest.rsi[0])
signalValues.insert(2, newest['%K'][0])
signalValues.insert(3, newest['%D'][0])
signalValues.insert(4, newest['macd'][0])
signalValues.insert(5, newest['support'][0])
signalValues.insert(6, newest['resistance'][0])
signalValues.insert(7, newest['buy_zone'][0])
signalValues.insert(8, newest['sell_zone'][0])
signalValues.insert(9, period)

def create_signals():
    with open(fileName, 'w') as f:
        write = csv.writer(f)
        write.writerow(header)
        write.writerow(signalValues)
        f.close()

def append_signals():
    with open(fileName, 'a+') as f:
        f.seek(0) # move read cursor to the start of file
        # if file is not empty then append '\n'
        data = f.read(100)
        if len(data) > 0:
            f.write("\n")
        # Append text at the end of file
        write = csv.writer(f)
        # write.writerow(header)
        write.writerow(signalValues)
        f.close()

# === CHECK if file exists ====
if file_exists(fileName):
    print("File bainaa baina: ", fileName)
    append_signals()
else:
    print("File OBSOO, we will create it: ", fileName)
    create_signals()

# === TODO: remove after test ===
# bot_signal = "sell"

# ===== save to SQL if signal is other than "WAIT" =====
if bot_signal == "buy" or bot_signal == "sell":
    print("BOT SIGNAL is other than WAIT, ==> ", bot_signal)
    # ===== INSERT into TradeSignals table ===
    if __name__ == "__main__":
        local_db_path = "../rails/trader/db/development.sqlite3"
        connection = sqlite3.connect(local_db_path)
        db_cursor = connection.cursor()
        new_signal = (period, now,rsi,k,d,macd,support,resistance,buy_zone,sell_zone,currency,bot_signal,last_close_price,now,now)

        # Insert into database
        sql = """INSERT INTO trade_signals(period, date,rsi,k,d,macd,support,resistance,buy_zone,sell_zone,currency,bot_signal,last_close_price,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        db_cursor.execute(sql, new_signal)

        connection.commit()
        connection.close()