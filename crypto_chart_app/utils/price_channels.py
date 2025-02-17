import pandas as pd
import numpy as np
from matplotlib import pyplot

def get_support_resistance(df, candle_groupow=20):
    backcandles= 50
    candle_group = 5
    candleid = 400

    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])
    for i in range(candleid-backcandles, candleid+1, candle_group):
        minim = np.append(minim, df.low.iloc[i:i+candle_group].min())
        xxmin = np.append(xxmin, df.low.iloc[i:i+candle_group].idxmin())
    for i in range(candleid-backcandles, candleid+1, candle_group):
        maxim = np.append(maxim, df.high.loc[i:i+candle_group].max())
        xxmax = np.append(xxmax, df.high.iloc[i:i+candle_group].idxmax())
    slmin, intercmin = np.polyfit(xxmin, minim,1)
    slmax, intercmax = np.polyfit(xxmax, maxim,1)

    dfpl = df[candleid-backcandles:candleid+backcandles]
    fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                    open=dfpl['open'],
                    high=dfpl['high'],
                    low=dfpl['low'],
                    close=dfpl['close'])])
    fig.add_trace(go.Scatter(x=xxmin, y=slmin*xxmin + intercmin, mode='lines', name='min slope'))
    fig.add_trace(go.Scatter(x=xxmax, y=slmax*xxmax + intercmax, mode='lines', name='max slope'))
    return df

def find_extremum(df, backcandles=30,candle_group=5):
    backcandles= 30
    candle_group = 5
    candleid = 400

    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])

    for i in range(0, len(df), candle_group):
        minim = np.append(minim, df.low.iloc[i:i+candle_group].min())
        xxmin = np.append(xxmin, df.low.iloc[i:i+candle_group].idxmin())
    # for i in range(candleid-backcandles, candleid+1, candle_group):
    for i in range(0, len(df), candle_group):
        maxim = np.append(maxim, df.high.loc[i:i+candle_group].max())
        xxmax = np.append(xxmax, df.high.iloc[i:i+candle_group].idxmax())
    slmin, intercmin = np.polyfit(xxmin, minim,1)
    slmax, intercmax = np.polyfit(xxmax, maxim,1)
    # Fitting intercepts to meet highest or lowest candle point in time slice
    # Цөөлсөн extremum цэгүүдийн дундаж утгыг авч adjintercmin, adjintercmax гэж тооцоолох
    adjintercmin = df.low.loc[candleid-backcandles:candleid].min() - slmin*df.low.iloc[candleid-backcandles:candleid].idxmin()
    adjintercmax = df.high.loc[candleid-backcandles:candleid].max() - slmax*df.high.iloc[candleid-backcandles:candleid].idxmax()
    # fig.add_trace(go.Scatter(x=xxmin, y=slmin*xxmin + adjintercmin, mode='lines', name='min slope'))
    # fig.add_trace(go.Scatter(x=xxmax, y=slmax*xxmax + adjintercmax, mode='lines', name='max slope'))
    # fig.show()
    return df

# ======================== NEW Technical Analysis Functions ========================
def support_resistance_range(df, price_range=5):
    # # Calculate resistance levels
    # resistance_range = abs(df['resistance'] - df['high'])
    # # Calculate support levels
    # support_range = abs(df['support'] - df['low'])
    # Add the new columns to the DataFrame
    df['near_support'] = df.apply(lambda row: row['low'] if abs(row['support'] - row['low']) <= price_range else None, axis=1)
    df['near_resistance'] = df.apply(lambda row: row['high'] if abs(row['resistance'] - row['high']) <= price_range else None, axis=1)
    return df