import pandas as pd
import numpy as np

def boilinger_band_check(df, window=20, num_std_dev=2, price_range=5):
    df['bb_middle'] = df['close'].rolling(window=window).mean()
    df['bb_std'] = df['close'].rolling(window=window).std()
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * num_std_dev)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * num_std_dev)
    df['bb_trend'] = 'wait'
    df['bb_signal'] = 'wait'
    
    for i in range(window, len(df)):
        if df['close'].iloc[i] > df['bb_upper'].iloc[i]:
            df.at[df.index[i], 'bb_trend'] = 'up'
            df.at[df.index[i], 'bb_signal'] = 'sell'
        elif df['close'].iloc[i] < df['bb_lower'].iloc[i]:
            df.at[df.index[i], 'bb_trend'] = 'down'
            df.at[df.index[i], 'bb_signal'] = 'buy'
        else:
            df.at[df.index[i], 'bb_trend'] = 'sideways'
            df.at[df.index[i], 'bb_signal'] = 'wait'
    # ================= new signal ===========================
    df['near_bb_support'] = df.apply(lambda row: row['low'] if (abs(row['bb_lower'] - row['low']) <= price_range or (row['rsi_trade'] == 'buy' and row['stochastic_trade'] == 'buy')) else None, axis=1)
    df['near_bb_resistance'] = df.apply(lambda row: row['high'] if (abs(row['bb_upper'] - row['high']) <= price_range or (row['rsi_trade'] == 'sell' and row['stochastic_trade'] == 'sell')) else None, axis=1)
    return df