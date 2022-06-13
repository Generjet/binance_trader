from pydoc import cli
from binance.spot import Spot
import os

# Get environment variables
api_key = os.getenv('API_KEY')
api_secret = os.environ.get('API_SECRET')

# client = Spot()
# print(client.time())

client = Spot(key=api_key, secret=api_secret)
print(client.account())
# Get account information
# print(client.account())

# # Post a new order
# params = {
#     'symbol': 'BTCUSDT',
#     'side': 'SELL',
#     'type': 'LIMIT',
#     'timeInForce': 'GTC',
#     'quantity': 0.002,
#     'price': 9500
# }

# response = client.new_order(**params)
# print(response)