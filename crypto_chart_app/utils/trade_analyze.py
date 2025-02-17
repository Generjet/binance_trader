import pandas as pd
import numpy as np


# ===================== Trade analyze functions =====================
def trade_analyze(analyzed_df):
    # Initialize the trade columns with 'wait'
    analyzed_df['macd_trade'] = 'wait'
    analyzed_df['rsi_trade'] = 'wait'
    analyzed_df['stochastic_trade'] = 'wait'
    analyzed_df['channel_trade'] = 'wait'
    analyzed_df['trade'] = 'wait'  # Add the new 'trade' column

    # Iterate over the DataFrame to determine trade signals
    for i in range(1, len(analyzed_df)):
        # # MACD trade signals
        # if analyzed_df['macd'].iloc[i] > analyzed_df['macd_signal'].iloc[i] and analyzed_df['macd'].iloc[i-1] <= analyzed_df['macd_signal'].iloc[i-1]:
        #     analyzed_df.at[analyzed_df.index[i], 'macd_trade'] = 'buy'
        # elif analyzed_df['macd'].iloc[i] < analyzed_df['macd_signal'].iloc[i] and analyzed_df['macd'].iloc[i-1] >= analyzed_df['macd_signal'].iloc[i-1]:
        #     analyzed_df.at[analyzed_df.index[i], 'macd_trade'] = 'sell'
        
        # RSI trade signals
        if analyzed_df['rsi'].iloc[i] < 30:
            analyzed_df.at[analyzed_df.index[i], 'rsi_trade'] = 'buy'
        elif analyzed_df['rsi'].iloc[i] > 70:
            analyzed_df.at[analyzed_df.index[i], 'rsi_trade'] = 'sell'
        
        # Stochastic oscillator trade signals
        if analyzed_df['stochastic-K'].iloc[i] < 20 and analyzed_df['stochastic-D'].iloc[i] < 20:
            analyzed_df.at[analyzed_df.index[i], 'stochastic_trade'] = 'buy'
        elif analyzed_df['stochastic-K'].iloc[i] > 80 and analyzed_df['stochastic-D'].iloc[i] > 80:
            analyzed_df.at[analyzed_df.index[i], 'stochastic_trade'] = 'sell'
        
        # Determine overall trade signal
        if not pd.isna(analyzed_df['near_bb_support'].iloc[i]) and analyzed_df['rsi_trade'].iloc[i] == 'buy' and analyzed_df['stochastic_trade'].iloc[i] == 'buy':
            analyzed_df.at[analyzed_df.index[i], 'channel_trade'] = 'buy'
        elif not pd.isna(analyzed_df['near_bb_resistance'].iloc[i]) and analyzed_df['rsi_trade'].iloc[i] == 'sell' and analyzed_df['stochastic_trade'].iloc[i] == 'sell':
            analyzed_df.at[analyzed_df.index[i], 'channel_trade'] = 'sell'
    
    return analyzed_df