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

# GENERJET API KEY and SECRET
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

client = Client(api_key, api_secret)

# # ====== get data function ======
# def fetchCryptoData(symbol, timePeriod ,lookback, ago='days ago UTC'):
#     frame = pd.DataFrame(client.get_historical_klines(symbol, timePeriod, lookback + ago ))
#     frame = frame.iloc[:,:6]
#     frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
#     frame.set_index('Time', inplace=True)
#     frame.index = pd.to_datetime(frame.index, unit='ms')
#     frame = frame.astype(float)
#     return frame

# # SHORT TERM data
# symbol = 'ETHUSDT'
# timePeriod = '30m'
# lookback = '60'
# min30 = fetchCryptoData(symbol, timePeriod, lookback )

# #LOGN TERM data

# symbol = 'ETHUSDT'
# timePeriod = '4h'
# lookback = '96'
# hour4 = fetchCryptoData(symbol, timePeriod, lookback )

# # print("Hour4", hour4)
# # return signal to shell
# print("wait")

# ===== UPDATE ROW ====
import csv

def update_csv_data(sell_date, sell_amount, sell_price):
    # Specify the path to your CSV file
    csv_file_path = "orders.csv"

    # Read data from CSV file and update rows if status matches "wait"
    updated_rows = []
    with open(csv_file_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames

        for row in reader:
            if row['sell_date'] == 'wait':
                row['sell_amount'] = str(sell_amount)
                row['sell_price'] = str(sell_price)
                row['sell_date'] = '2023-07-28 06:30:00'
            updated_rows.append(row)

    # Write the updated data back to the CSV file, overwriting the existing contents
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

# Example usage:
sell_date = "wait"
sell_amount = 0.66
sell_price = 2025.99
update_csv_data(sell_date, sell_amount, sell_price)