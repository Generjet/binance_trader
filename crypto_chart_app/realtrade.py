# АЛХАМУУД
# 1. Шинээр дата татаад шууд датабазад хадгалах, ингэснээр ID үүснэ
# 2. RESISTANCE and SUPPORT тодорхойлж датабаз руу ID-аар нь шүүд хадгална.

# Data fetching
from utils.get_data import fetchCryptoData
import os
import time
import sys
from tabulate import tabulate

symbol = 'ETHUSDT'
timePeriod = '1h'
lookback = 200
df = fetchCryptoData(symbol, timePeriod, lookback)
print(df.tail())

from utils.apply_technicals import apply_technicals
from utils.candle_patterns import detect_engulfing_pattern
from utils.price_channels import find_extremum
from utils.price_channels import support_resistance_range
from utils.trade_analyze import trade_analyze
from utils.boilinger_band import boilinger_band_check
from utils.save2mysql import create_database_if_not_exists
from utils.save2mysql import update_db
import pandas as pd
import numpy as np

# Analyzing
analyzed_df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume','support', 'resistance','macd','macd_signal','macd_hist','rsi','stochastic-K','stochastic-D','ema','bb_middle','bb_std','bb_upper','bb_lower','bb_trend','bb_signal','near_support','near_resistance','engulfing','reversal','doji','macd_trade','rsi_trade','stochastic_trade','channel_trade','near_bb_support','near_bb_resistance', 'trade'])
# Add the necessary columns if they do not exist
if 'support' not in df.columns:
    df['support'] = np.nan
if 'resistance' not in df.columns:
    df['resistance'] = np.nan
if 'macd' not in df.columns:
    df['macd'] = np.nan
if 'macd_signal' not in df.columns:
    df['macd_signal'] = np.nan
if 'macd_hist' not in df.columns:
    df['macd_hist'] = np.nan
if 'rsi' not in df.columns:
    df['rsi'] = np.nan
if 'stochastic-K' not in df.columns:
    df['stochastic-K'] = np.nan
if 'stochastic-D' not in df.columns:
    df['stochastic-D'] = np.nan
if 'ema' not in df.columns:
    df['ema'] = np.nan
if 'bb_middle' not in df.columns:
    df['bb_middle'] = np.nan
if 'bb_std' not in df.columns:
    df['bb_std'] = np.nan
if 'bb_upper' not in df.columns:
    df['bb_upper'] = np.nan
if 'bb_lower' not in df.columns:
    df['bb_lower'] = np.nan
if 'bb_trend' not in df.columns:
    df['bb_trend'] = np.nan
if 'bb_signal' not in df.columns:
    df['bb_signal'] = np.nan
if 'near_support' not in df.columns:
    df['near_support'] = np.nan
if 'near_resistance' not in df.columns:
    df['near_resistance'] = np.nan
if 'engulfing' not in df.columns:
    df['engulfing'] = 'no'
if 'reversal' not in df.columns:
    df['reversal'] = 'no'
if 'doji' not in df.columns:
    df['doji'] = 'no'
if 'macd_trade' not in df.columns:
    df['macd_trade'] = 'wait'
if 'rsi_trade' not in df.columns:
    df['rsi_trade'] = 'wait'
if 'stochastic_trade' not in df.columns:
    df['stochastic_trade'] = 'wait'
if 'channel_trade' not in df.columns:
    df['channel_trade'] = 'wait'
if 'near_bb_support' not in df.columns:
    df['near_bb_support'] = np.nan
if 'near_bb_resistance' not in df.columns:
    df['near_bb_resistance'] = np.nan
if 'trade' not in df.columns:
    df['trade'] = 'wait'
# === create database if not exists ===
create_database_if_not_exists()
print("Database created")
for index, row in df.iterrows():
    # for index, row in df.iterrows(): нь historical data-г нэг нэгээр авч байгаа simulation
    analyzed_df = df.iloc[0:index+1].copy()

    if len(analyzed_df) > 4: # call support_resistance_range after find_extremum
        # analyzed_df = support_resistance_range(analyzed_df, 10)
        analyzed_df = detect_engulfing_pattern(analyzed_df)
    if len(analyzed_df) > 20:
        analyzed_df = apply_technicals(analyzed_df)
        analyzed_df = boilinger_band_check(analyzed_df,20, 2, 10)
        # print(tabulate(analyzed_df[['time', 'engulfing','macd_hist', 'macd_trade', 'rsi_trade', 'stochastic_trade', 'channel_trade', 'bb_trend', 'bb_signal']].tail(4), headers='keys', tablefmt='psql', floatfmt='.4f'))
    update_db(row)
    latest_row = analyzed_df.iloc[-1]
    update_db(latest_row)
print("Analysis completed")
print(analyzed_df.tail(10))