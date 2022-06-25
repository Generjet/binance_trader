import os
import sys
from matplotlib.pyplot import get
import pandas as pd
from binance.client import Client
import ta

# GENERJET API KEY and SECRET
api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')
print("API_KEY=",api_key)
print("API_SECRET=", api_secret)

client = Client(api_key, api_secret)

# минутын дата авах
def getMinuteData(symbol):
    df = pd.DataFrame(client.get_historical_klines(symbol,'1m','40m UTC'))
    # get only first 6 columns: time, open, close, high, low, VOLUME
    df = df.iloc[:,:6]
    df.columns = ['Time', 'Open', 'High','Low','Close', 'VOLUME']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df
    # pd.DataFrame(client.klines(symbol,'1h',limit=10))
    # frame = pd.DataFrame(client.get_historical_klines(symbol,'1h','25 hours ago UTC'))
    # frame = frame.iloc[:,:5]
    # frame.columns = ['Time', 'Open', 'High','Low','Close']
    # frame.Time = pd.to_datetime(frame.Time, unit='ms')
    # return frame

minuteData = getMinuteData('ETHUSDT')
print(minuteData)

# === Trading strategy ===
def tradingStrat(symbol, qty, open_position = False):
    # BUY ===== condition
    while True:
        df = getMinuteData(symbol)
        if not open_position:
            # Check the last row of data, so that MACD difference is above 0.
            # Also the row before last row has MACD difference is not larger than zero
            # Simply: MACD-diff-Row[-1] > 0 && MACD-diff-Row[-2] < 0
            if ta.trend.macd_diff(df.Close).iloc[-1] > 0 \
                and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
                order = client.create_order(symbol=symbol,side='BUY',type='MARKET',quantity=qty)
                print(order)
                # Захиалга/BUY хийгдмэгц, BUY захиалга хийгдсэн тэмдэг тавина open_position = True
                open_position = True
                buyprice = float(order['fills'][0]['price'])
                # Нэгэнт BUY хийсэн учир дахин дата дуудаж MACD check and buy function ажиллуулах хэрэггүй тул давталтаас гарна
                break
    # SELL ===== condition
    if open_position:
        while True:
            df = getMinuteData(symbol)
            # Action is same as above BUY, but in reverse way
            # Simply: MACD-diff-Row[-1] < 0 && MACD-diff-Row[-2] > 0
            if ta.trend.macd_diff(df.Close).iloc[-1] < 0 \
                and ta.trend.macd_diff(df.Close).iloc[-2] > 0:
                order = client.create_order(symbol=symbol,side='SELL',type='MARKET',quantity=qty)
                print(order)
                sellprice = float(order['fills'][0]['price'])
                # === Ашиг хэвлэх =====
                profit = (sellprice - buyprice)/buyprice
                print("Profit = "+profit)
                # Захиалга/SELL хийгдмэгц, BUY захиалга finished result тул тэмдэг тавина open_position = True
                open_position = False
                break

# if you want to run only once, then run it without "while True:", but if you want to run continiously then run within "while True:"
while True:
    tradingStrat('ETHUSDT', qty=0.01)
sys.exit()

# крипто авах захиалга өөрчлөх

# exit in the middle for DEBUG
# sys.exit()