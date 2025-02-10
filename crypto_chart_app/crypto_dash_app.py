import dash
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
import plotly.graph_objs as go
import pandas as pd
from sqlalchemy import create_engine
import time

# Database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tamir4578',
    'database': 'portalblog_dev'
}

table_name = 'analyzed_data'
timestamp_col = 'time'
open_col = 'open'
high_col = 'high'
low_col = 'low'
close_col = 'close'

# Create database connection string
db_connection_str = 'mysql+pymysql://{user}:{password}@{host}/{database}'.format(**db_config)
db_connection = create_engine(db_connection_str)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=2*1000, # in milliseconds
        n_intervals=0
    ),
    dcc.Graph(id='candlestick-chart'),
    dcc.Graph(id='macd-chart'),
    dcc.Graph(id='rsi-chart'),
    dcc.Graph(id='stochastic-chart'),
    html.Div([
        html.Div([
            html.Div([
                html.Label('Window Size:', style={'margin-right': '10px'}),
                dcc.Input(
                    id='window-size-input',
                    type='number',
                    value=100,
                    min=50,
                    max=1000,
                    step=50,
                    debounce=True,
                    style={'width': '100px', 'margin-right': '20px'}
                ),
            ], style={'flex': '1', 'margin-right': '20px'}),
            html.Div([
                html.Label('Date Range:', style={'margin-right': '10px'}),
                dcc.DatePickerRange(
                    id='date-picker',
                    start_date=pd.Timestamp.now() - pd.DateOffset(days=7),
                    end_date=pd.Timestamp.now(),
                    display_format='YYYY-MM-DD',
                    style={'width': '300px'}
                )
            ], style={'flex': '1', 'margin-left': '20px'}),
        ], style={'display': 'flex', 'align-items': 'center', 'margin': '10px'})
    ]),
])

def fetch_data_from_db(window_size=100, start_date=None, end_date=None):
    query = f'SELECT * FROM (SELECT * FROM {table_name} ORDER BY {timestamp_col} DESC LIMIT {window_size}) AS recent_data'
    if start_date and end_date:
        query = f'SELECT * FROM (SELECT * FROM {table_name} WHERE {timestamp_col} BETWEEN "{start_date}" AND "{end_date}" ORDER BY {timestamp_col} DESC LIMIT {window_size}) AS recent_data'
    query += f' ORDER BY {timestamp_col} ASC'
    df = pd.read_sql(query, db_connection)
    return df

def create_candlestick_chart(df):
    candlestick = go.Candlestick(
        x=df[timestamp_col],
        open=df[open_col],
        high=df[high_col],
        low=df[low_col],
        close=df[close_col],
        name='Candlestick'
    )

    ema_line = go.Scatter(
        x=df[timestamp_col],
        y=df['ema'], # Assuming 'ema' column exists
        name='EMA',
        line=dict(color='blue')
    )

    support_line = go.Scatter(
        x=df[timestamp_col],
        y=df['support'], # Assuming 'support' column exists
        name='Support',
        line=dict(color='green', dash='dash')
    )

    resistance_line = go.Scatter(
        x=df[timestamp_col],
        y=df['resistance'], # Assuming 'resistance' column exists
        name='Resistance',
        line=dict(color='red', dash='dash')
    )

    near_support_points = go.Scatter(
        x=df[timestamp_col],
        y=df['near_support'], # Assuming 'near_support' column exists
        mode='markers',
        marker=dict(color='green', symbol='circle', size=5),
        name='Near Support'
    )

    near_resistance_points = go.Scatter(
        x=df[timestamp_col],
        y=df['near_resistance'], # Assuming 'near_resistance' column exists
        mode='markers',
        marker=dict(color='red', symbol='circle', size=5),
        name='Near Resistance'
    )

    engulfing_points = go.Scatter(
        x=df[timestamp_col],
        y=df['engulfing'], # Assuming 'engulfing' column exists
        mode='markers',
        marker=dict(color='yellow', symbol='star', size=10),
        name='Engulfing'
    )

    bb_upper_line = go.Scatter(
        x=df[timestamp_col],
        y=df['bb_upper'], # Assuming 'bb_upper' column exists
        name='BB Upper',
        line=dict(color='purple', dash='dash')
    )

    bb_middle_line = go.Scatter(
        x=df[timestamp_col],
        y=df['bb_middle'], # Assuming 'bb_middle' column exists
        name='BB Middle',
        line=dict(color='orange', dash='dash')
    )

    bb_lower_line = go.Scatter(
        x=df[timestamp_col],
        y=df['bb_lower'], # Assuming 'bb_lower' column exists
        name='BB Lower',
        line=dict(color='purple', dash='dash')
    )

    # Shift x-axis to the right to show last 300 candles clearly
    if len(df) > 300:
        x_range = [df[timestamp_col].iloc[-300], df[timestamp_col].iloc[-1]]
    else:
        x_range = [df[timestamp_col].iloc[0], df[timestamp_col].iloc[-1]]


    layout = go.Layout(
        title='Candlestick Chart with EMA, Support and Resistance',
        xaxis=dict(title='Time',
                   range=x_range), # Set x-axis range
        yaxis=dict(title='Price')
    )

    fig = go.Figure(data=[candlestick, ema_line, support_line, resistance_line, near_support_points, near_resistance_points, engulfing_points, bb_upper_line, bb_middle_line, bb_lower_line], layout=layout)
    return fig

def create_macd_chart(df):
    macd_line = go.Scatter(
        x=df[timestamp_col],
        y=df['macd'], # Assuming 'macd' column exists
        name='MACD Line',
        marker_color='blue'
    )
    signal_line = go.Scatter(
        x=df[timestamp_col],
        y=df['macd_signal'], # Assuming 'macd_signal' column exists
        name='Signal Line',
        marker_color='red'
    )
    hist = go.Bar(
        x=df[timestamp_col],
        y=df['macd_hist'], # Assuming 'macd_hist' column exists
        name='Histogram',
        marker_color='grey'
    )
    layout = go.Layout(
        title='MACD',
        xaxis=dict(title='Time', showticklabels=False), # Hide x-axis labels
        yaxis=dict(title='MACD Value')
    )
    fig = go.Figure(data=[macd_line, signal_line, hist], layout=layout)
    return fig

def create_rsi_chart(df):
    rsi_line = go.Scatter(
        x=df[timestamp_col],
        y=df['rsi'], # Assuming 'rsi' column exists
        name='RSI'
    )
    layout = go.Layout(
        title='RSI',
        xaxis=dict(title='Time', showticklabels=False), # Hide x-axis labels
        yaxis=dict(title='RSI Value'),
        yaxis_range=[0, 100]
    )
    fig = go.Figure(data=[rsi_line], layout=layout)
    return fig

def create_stochastic_chart(df):
    stochastic_k = go.Scatter(
        x=df[timestamp_col],
        y=df['stochastic_K'], # Assuming 'stochastic_K' column exists
        name='%K'
    )
    stochastic_d = go.Scatter(
        x=df[timestamp_col],
        y=df['stochastic_D'], # Assuming 'stochastic_D' column exists
        name='%D'
    )
    layout = go.Layout(
        title='Stochastic Oscillator',
        xaxis=dict(title='Time', showticklabels=False), # Hide x-axis labels
        yaxis=dict(title='Stochastic Value'),
        yaxis_range=[0, 100]
    )
    fig = go.Figure(data=[stochastic_k, stochastic_d], layout=layout)
    return fig


@app.callback(
    [dash.dependencies.Output('candlestick-chart', 'figure'),
     dash.dependencies.Output('macd-chart', 'figure'),
     dash.dependencies.Output('rsi-chart', 'figure'),
     dash.dependencies.Output('stochastic-chart', 'figure')],
    [dash.dependencies.Input('interval-component', 'n_intervals'),
     dash.dependencies.Input('window-size-input', 'value'),
     dash.dependencies.Input('date-picker', 'start_date'),
     dash.dependencies.Input('date-picker', 'end_date')]
)
def update_charts(n, window_size, start_date, end_date):
    df = fetch_data_from_db(window_size=window_size, start_date=start_date, end_date=end_date)
    candlestick_fig = create_candlestick_chart(df)
    macd_fig = create_macd_chart(df)
    rsi_fig = create_rsi_chart(df)
    stochastic_fig = create_stochastic_chart(df)
    return candlestick_fig, macd_fig, rsi_fig, stochastic_fig

if __name__ == '__main__':
    app.run_server(debug=True)