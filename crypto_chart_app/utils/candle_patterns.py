import numpy as np
import pandas as pd

# Trend reversal patterns
def detect_engulfing_pattern(df):
    if len(df) < 4:
        df['engulfing'] = 'no'
        df['reversal'] = 'no'
        df['doji'] = 'no'
        return df

    df['engulfing'] = 'no'
    df['reversal'] = 'no'
    df['doji'] = 'no'
    for i in range(3, len(df)):
        prev_candle = df.iloc[i-1]
        current_candle = df.iloc[i]
        prev_trend = df.iloc[i-2]['close'] - df.iloc[i-3]['close']
        # prev_trend negative means downtrend, positive means uptrend

        doji_type = doji_check(prev_candle)
        reversal = reversal_pattern(prev_candle)
        df.at[i-1, 'reversal'] = reversal  # Save the reversal pattern in the DataFrame
        df.at[i-1, 'doji'] = doji_type  # Save the doji type in the DataFrame
        # ======================== NEW CODE ========================
        if doji_type == "bullish_doji" or reversal == "bullish_hammer" or reversal == "bullish_inverted_hammer":
            if prev_trend < 0 and current_candle['close'] > current_candle['open'] and current_candle['close'] > prev_candle['close'] and current_candle['open'] > prev_candle['low']:
                df.at[i, 'engulfing'] = 'bullish'
        elif doji_type == "bearish_doji" or reversal == "bearish_shooting_star" or reversal == "bearish_hanging_man":
            if prev_trend > 0 and current_candle['close'] < current_candle['open'] and current_candle['close'] < prev_candle['close'] and current_candle['open'] < prev_candle['high']:
                df.at[i, 'engulfing'] = 'bearish'
        # ======================== OLD CODE ========================
        # if doji_type == "bullish_doji" or reversal == "bullish_hammer" or reversal == "bullish_inverted_hammer":
        #     if prev_trend < 0 and current_candle['close'] > current_candle['open'] and current_candle['close'] > prev_candle['high'] and current_candle['open'] < prev_candle['low']:
        #         df.at[i, 'engulfing'] = 'bullish'
        # elif doji_type == "bearish_doji" or reversal == "bearish_shooting_star" or reversal == "bearish_hanging_man":
        #     if prev_trend > 0 and current_candle['close'] < current_candle['open'] and current_candle['close'] < prev_candle['low'] and current_candle['open'] > prev_candle['high']:
        #         df.at[i, 'engulfing'] = 'bearish'

    return df

def doji_check(candle):
    open_price = candle['open']
    close_price = candle['close']
    high_price = candle['high']
    low_price = candle['low']
    # Check if the candlestick is a Doji
    is_doji = abs(open_price - close_price) / (high_price - low_price) < 0.1 if (high_price - low_price) > 0 else False
    if not is_doji:
        return "no"
    # Check if the Doji is bullish or bearish
    if close_price > open_price:
        return "bullish_doji"
    elif open_price > close_price:
        return "bearish_doji"
    return "no"

def reversal_pattern(candle):
    open_price = candle['open']
    close_price = candle['close']
    high_price = candle['high']
    low_price = candle['low']
    body_length = abs(close_price - open_price)
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price

    # Bullish patterns
    if body_length <= (high_price - low_price) * 0.3:
        if lower_shadow >= 2 * body_length and upper_shadow <= body_length:
            if close_price > open_price:
                return "bullish_hammer"
            elif open_price > close_price:
                return "bullish_inverted_hammer"

    # Bearish patterns
    if body_length <= (high_price - low_price) * 0.3:
        if upper_shadow >= 2 * body_length and lower_shadow <= body_length:
            if open_price > close_price:
                return "bearish_shooting_star"
            elif close_price > open_price:
                return "bearish_hanging_man"

    return "no"