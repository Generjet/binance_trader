from binance.spot import Spot
import os
import ta

client = Spot()
# GENERJET API KEY and SECRET
API_KEY = os.getenv('bot_api_key')
API_SECRET = os.getenv('bot_api_secret')
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