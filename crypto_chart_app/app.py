from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import plotly.graph_objects as go
from flask_socketio import SocketIO, emit
from save2mysql import db, AnalyzedData
import time

app = Flask(__name__, static_folder='static')
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

        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            title='Crypto Price Data',
            yaxis_title='Price',
            xaxis_title='Time'
        )

        chart_html = fig.to_html(full_html=False)
        table_html = df.head(30).to_html(classes='data', index=False, border=0)

        latest_data = df.iloc[0].to_dict() if not df.empty else {}

        return render_template('index.html', chart_html=chart_html, table_data=table_html, latest_data=latest_data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def emit_latest_data():
    with app.app_context():
        latest_data = AnalyzedData.query.order_by(AnalyzedData.time.desc()).first()
        if latest_data:
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
        time.sleep(5)

if __name__ == '__main__':
    socketio.start_background_task(check_for_new_data)
    socketio.run(app, debug=True, host='0.0.0.0')
