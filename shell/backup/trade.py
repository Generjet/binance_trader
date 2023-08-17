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
from os.path import exists as file_exists

# GENERJET API KEY and SECRET
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

client = Client(api_key, api_secret)

# === read signals.csv ===
signals = pd.read_csv('signals.csv')
# ==== read orders.csv ===
orders = pd.read_csv('orders.csv')
print('ORDERS ', orders)

# # === CHECK previous OPEN orders ===
# sorted_orders = orders.sort_values(by=['buy_date'])
# isSold = sorted_orders.loc[sorted_orders['sell_amount'] == 'no' ]
# if isSold == 'no':
#     open_buy = True
# else:
#     open_buy = False


# === CHECK signals ===
buy_signal = False
sell_signal = False

# === CREATE ORDER ===
# if (open_buy == False) & ( buy_signal == True):
#     print("CURRENTLY no OPEN BUY and we have BUY SIGNAL => WE CAN BUY NOW")
#     signal = 'buy'
# elif (current['Close'][0] < longTerm['support'][0]) & (longTerm['rsi'][0] < 30 ):
#     print("BREAKOUT SELL TRUE")
#     breakout_buy = False
#     signal = 'sell'


# ===== INSERT INTO ORDERS.CSV =========
now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
fileName = 'orders.csv'

# === PREPARE signals ROW ====
# newest = hour4.tail(1)
header = ['buy_amount','buy_price','buy_date','sell_amount','sell_price','sell_date']
buy_amount = 0.89
buy_price = 1832
buy_date = now
sell_amount = 0.89
sell_price = 4560
sell_date = now

# ===== INSERT INTO SQLITE ORDERS TABLE  =====
import sqlite3

if __name__ == "__main__":
    local_db_path = "../rails/trader/db/development.sqlite3"
    connection = sqlite3.connect(local_db_path)
    db_cursor = connection.cursor()

    new_order = (buy_amount, buy_price,buy_date,sell_amount,sell_price,sell_date, now, now)

    # Insert into database
    sql = """INSERT INTO orders('buy_amount','buy_price','buy_date','sell_amount','sell_price','sell_date', 'created_at', 'updated_at')
             VALUES(?,?,?,?,?,?,?,?)"""
    db_cursor.execute(sql, new_order)

    connection.commit()
    connection.close()

# orderValues  = []
# orderValues.insert(0,now)
# orderValues.insert(1, newest.rsi[0])
# orderValues.insert(2, newest['%K'][0])
# orderValues.insert(3, newest['%D'][0])
# orderValues.insert(4, newest['macd'][0])
# orderValues.insert(5, newest['support'][0])
# orderValues.insert(6, newest['resistance'][0])
# orderValues.insert(7, newest['buy_zone'][0])
# orderValues.insert(8, newest['sell_zone'][0])

# def create_orders():
#     with open(fileName, 'w') as f:
#         write = csv.writer(f)
#         write.writerow(header)
#         write.writerow(orderValues)
#         f.close()

# def append_orders():
#     with open(fileName, 'a+') as f:
#         f.seek(0) # move read cursor to the start of file
#         # if file is not empty then append '\n'
#         data = f.read(100)
#         if len(data) > 0:
#             f.write("\n")
#         # Append text at the end of file
#         write = csv.writer(f)
#         # write.writerow(header)
#         write.writerow(orderValues)
#         f.close()

# # === CHECK if file exists ====
# if file_exists(fileName):
#     print("File bainaa baina: ", fileName)
#     append_signals()
# else:
#     print("File OBSOO, we will create it: ", fileName)
#     create_signals()