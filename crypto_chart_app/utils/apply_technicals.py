import pandas as pd
import ta

def apply_technicals(df):
    if len(df) < 14:  # Minimum required length for calculations
        return df    
    df_tech = df.copy()
    try:
        # Calculate MACD
        # Calculate short and long EMA
        short_ema = df_tech['close'].ewm(span=12, adjust=False).mean()
        long_ema = df_tech['close'].ewm(span=32, adjust=False).mean()
        # Calculate MACD and MACD Signal
        # df_tech['macd'] = ta.trend.macd(df_tech['close'])
        # df_tech['macd_signal'] = ta.trend.macd_signal(df_tech['close'])
        # df_tech['macd_hist'] = ta.trend.macd_diff(df_tech['close'])
        # Calculate RSI
        df_tech['rsi'] = ta.momentum.rsi(df_tech['close'], window=14)
        # Calculate Stochastic Oscillator
        df_tech['stochastic-K'] = ta.momentum.stoch(df_tech['high'], df_tech['low'], df_tech['close'], window=14, smooth_window=3)
        df_tech['stochastic-D'] = df_tech['stochastic-K'].rolling(3).mean()
        # Calculate EMA
        df_tech['ema'] = df_tech['close'].ewm(span=14, adjust=False).mean()
        df_tech = boilinger_band_check(df_tech, 20, 2, 10) # boilinger_band_check(df, window=20, num_std_dev=2, price_range=5):
        # Fill NaN values with previous values
        df_tech = df_tech.ffill()
    except Exception as e:
        print(f"Error in technical analysis: {e}")
        return df
    
    return df_tech