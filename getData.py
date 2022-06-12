import pandas as pd
import sqlalchemy
from binance.client import Client
from binance import BinanceSocketManager

from binance import *

import os
import sys

# GENERJET API KEY and SECRET
api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')
print("API_KEY=",api_key)
print("API_SECRET=", api_secret)

# exit in the middle for DEBUG
# sys.exit()

client = Client(api_key, api_secret)
# create Binance Socket Manager
bsm = BinanceSocketManagaer(client)
socket = bsm.trade_socket('BTCUSDT')

async def getData():
    await socket.__aenter__()
    msg = await socket.recv()
    print(msg)

while True:
    getData()