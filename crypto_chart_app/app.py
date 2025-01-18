from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import plotly.graph_objects as go
from flask_socketio import SocketIO, emit
from save2mysql import db, AnalyzedData
import time

app = Flask(__name__, static_folder='static', static_url_path='/static')
app._static_folder = 'static'
app.add_url_rule('/assets/<path:filename>', endpoint='assets', view_func=app.send_static_file)
CORS(app)
socketio = SocketIO(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Tamir4578@localhost/portalblog_dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    with app.app_context():
        data = AnalyzedData.query.order_by(AnalyzedData.time.desc()).limit(100).all()
        if not data:
            return "No data found", 404

        df = pd.DataFrame([{
            'time': d.time,
            'open': d.open,
            'high': d.high,
            'low': d.low,
            'close': d.close,
            'volume': d.volume,
            'resistance': d.resistance,
            'support': d.support,
            'macd': d.macd,
            'rsi': d.rsi,
            'ema': d.ema,
            'stochastic_D': d.stochastic_D,
            'stochastic_K': d.stochastic_K
        } for d in data])

        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='green',
            decreasing_line_color='red'
        )])

        # Add EMA, resistance, and support to the candlestick chart
        fig.add_trace(go.Scatter(x=df['time'], y=df['ema'], mode='lines', name='EMA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df['time'], y=df['resistance'], mode='lines', name='Resistance', line=dict(color='orange', dash='dash')))
        fig.add_trace(go.Scatter(x=df['time'], y=df['support'], mode='lines', name='Support', line=dict(color='red', dash='dash')))

        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            title='Crypto Price Data',
            yaxis=dict(title='Price', color='white'),
            xaxis=dict(title='Time', color='white'),
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )

        chart_html = fig.to_html(full_html=False)

        # Create volume chart
        volume_fig = go.Figure(data=[go.Bar(
            x=df['time'],
            y=df['volume'],
            name='Volume',
            marker=dict(color=df.apply(lambda row: 'green' if row['close'] > row['open'] else 'red', axis=1))
        )])
        volume_fig.update_layout(
            template='plotly_dark',
            title='Volume',
            yaxis=dict(title='Volume', color='white'),
            xaxis=dict(title='Time', color='white'),
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        volume_chart_html = volume_fig.to_html(full_html=False)

        # Create MACD chart
        macd_fig = go.Figure(data=[go.Scatter(x=df['time'], y=df['macd'], mode='lines', name='MACD', line=dict(color='cyan'))])
        macd_fig.update_layout(
            template='plotly_dark',
            title='MACD',
            yaxis=dict(title='MACD', color='white'),
            xaxis=dict(title='Time', color='white'),
            shapes=[
                { 'type': 'line', 'x0': 0, 'x1': 1, 'y0': 20, 'y1': 20, 'xref': 'paper', 'yref': 'y', 'line': { 'color': 'red', 'dash': 'dash' } },
                { 'type': 'line', 'x0': 0, 'x1': 1, 'y0': 80, 'y1': 80, 'xref': 'paper', 'yref': 'y', 'line': { 'color': 'red', 'dash': 'dash' } },
                { 'type': 'line', 'x0': 0, 'x1': 1, 'y0': 0, 'y1': 0, 'xref': 'paper', 'yref': 'y', 'line': { 'color': 'white', 'dash': 'dash' } }
            ],
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        macd_chart_html = macd_fig.to_html(full_html=False)

        # Create RSI chart
        rsi_fig = go.Figure(data=[go.Scatter(x=df['time'], y=df['rsi'], mode='lines', name='RSI', line=dict(color='magenta'))])
        rsi_fig.update_layout(
            template='plotly_dark',
            title='RSI',
            yaxis=dict(title='RSI', color='white'),
            xaxis=dict(title='Time', color='white'),
            shapes=[
                { 'type': 'line', 'x0': 0, 'x1': 1, 'y0': 20, 'y1': 20, 'xref': 'paper', 'yref': 'y', 'line': { 'color': 'red', 'dash': 'dash' } },
                { 'type': 'line', 'x0': 0, 'x1': 1, 'y0': 80, 'y1': 80, 'xref': 'paper', 'yref': 'y', 'line': { 'color': 'red', 'dash': 'dash' } }
            ],
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        rsi_chart_html = rsi_fig.to_html(full_html=False)

        # Create Stochastic chart
        stochastic_fig = go.Figure()
        stochastic_fig.add_trace(go.Scatter(x=df['time'], y=df['stochastic_K'], mode='lines', name='Stochastic %K', line=dict(color='yellow')))
        stochastic_fig.add_trace(go.Scatter(x=df['time'], y=df['stochastic_D'], mode='lines', name='Stochastic %D', line=dict(color='red')))
        stochastic_fig.update_layout(
            template='plotly_dark',
            title='Stochastic',
            yaxis=dict(title='Stochastic', color='white'),
            xaxis=dict(title='Time', color='white'),
            shapes=[
                { 'type': 'line', 'x0': 0, 'x1': 1, 'y0': 20, 'y1': 20, 'xref': 'paper', 'yref': 'y', 'line': { 'color': 'red', 'dash': 'dash' } },
                { 'type': 'line', 'x0': 0, 'x1': 1, 'y0': 80, 'y1': 80, 'xref': 'paper', 'yref': 'y', 'line': { 'color': 'red', 'dash': 'dash' } }
            ],
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        stochastic_chart_html = stochastic_fig.to_html(full_html=False)

        table_html = df.head(30).to_html(classes='data', index=False, border=0)

        latest_data = df.iloc[0].to_dict() if not df.empty else {}

        return render_template('index.html', chart_html=chart_html, volume_chart_html=volume_chart_html, macd_chart_html=macd_chart_html, rsi_chart_html=rsi_chart_html, stochastic_chart_html=stochastic_chart_html, table_data=table_html, latest_data=latest_data, df=df)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def check_for_new_data():
    last_time = None
    while True:
        with app.app_context():
            latest_data = AnalyzedData.query.order_by(AnalyzedData.time.desc()).first()
            if latest_data and latest_data.time != last_time:
                last_time = latest_data.time
                data = {
                    'time': latest_data.time,
                    'open': latest_data.open,
                    'high': latest_data.high,
                    'low': latest_data.low,
                    'close': latest_data.close,
                    'volume': latest_data.volume,
                    'resistance': latest_data.resistance,
                    'support': latest_data.support,
                    'macd': latest_data.macd,
                    'rsi': latest_data.rsi,
                    'ema': latest_data.ema,
                    'stochastic_D': latest_data.stochastic_D,
                    'stochastic_K': latest_data.stochastic_K
                }
                socketio.emit('new_data', data)
        time.sleep(2)

if __name__ == '__main__':
    socketio.start_background_task(check_for_new_data)
    socketio.run(app, debug=True, host='0.0.0.0')
