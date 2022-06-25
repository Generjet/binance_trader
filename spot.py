import pandas as pd
import os
import sys

# client = Spot()

# GENERJET API KEY and SECRET
api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')
print("API_KEY=",api_key)
print("API_SECRET=", api_secret)

# api key/secret are required for user data endpoints
client = Spot(key=api_key, secret=api_secret)
# binance.options['adjustForTimeDifference'] = true

# Get account and balance information
accountType = client.account()["accountType"]
balanceBTC = client.account()["balances"][0]
balanceETH = client.account()["balances"][1]
balanceBNB = client.account()["balances"][5]
balanceUSDT = client.account()["balances"][12]
# print(client.account())
print(balanceBTC)
print(balanceETH)
print(balanceBNB)
print(balanceUSDT)

sys.exit()



# Get server timestamp
print(client.time())

# Get Klines data
data1m = client.klines("ETHUSDT", "1m")

# цагийн дата авах
def gethourlydata(symbol):
    # frame = pd.DataFrame(client.klines(symbol,'1h','25 hours ago UTC'))
    frame = pd.DataFrame(client.klines(symbol,'1h',limit=10))
    frame = frame.iloc[:,:5]
    frame.columns = ['Time', 'Open', 'High','Low','Close']
    frame.Time = pd.to_datetime(frame.Time, unit='ms')
    return frame

hourData = gethourlydata("ETHUSDT")
print("HOURLY DATA 1m ==== >")
print(hourData)
print("HOURLY DATA 1m ==== >")

sys.exit()

#  Order params
# params = {
#     'symbol': 'BTCUSDT',
#     'side': 'SELL',
#     'type': 'LIMIT',
#     'timeInForce': 'GTC',
#     'quantity': 0.002,
#     'price': 9500
# }
# def placeOrder():
#     # Post a new order
#     params = {
#         'symbol': 'ETHUSDT',
#         'side': 'SELL',
#         'type': 'LIMIT',
#         'timeInForce': 'GTC',
#         'quantity': 0.002,
#         'price': 1400
#     }

