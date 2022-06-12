import os
import sys
from binance import client
import pandas as pd

# GENERJET API KEY and SECRET
api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')
print("API_KEY=",api_key)
print("API_SECRET=", api_secret)

# POSITION data of current, крипто авах лист
posframe = pd.read_csv('position.csv')
print(posframe)

# крипто авах захиалга өөрчлөх
def changepos(curr, buy=True):
    if buy:
        posframe.loc[posframe.Currency == curr, 'position'] = 1
    else:
        posframe.loc[posframe.Currency == curr, 'position'] = 0
    
    posframe.to_csv('position', index=False)

# цагийн дата авах
def gethourlydata(symbol):
    frame = pd.DataFrame(client.get_historical_klines(symbol,'1h','25 hours ago UTC'))
    frame = frame.iloc[:,:5]
    frame.columns = ['Time', 'Open', 'High','Low','Close']
    frame.Time = pd.to_datetime(frame.Time, unit='ms')
    return frame

hourlyData = gethourlydata('BTCUSDT')
print(hourlyData)
# exit in the middle for DEBUG
# sys.exit()