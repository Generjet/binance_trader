from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import requests
import time
import threading

app = Flask(__name__, static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

current_data = []
data_lock = threading.Lock()

def find_extremum(data):
    extremum_points = []
    window = 5
    for i in range(window, len(data) - window):
        is_max = all(data[i]['high'] > data[j]['high'] for j in range(i - window, i + window + 1) if j != i)
        is_min = all(data[i]['low'] < data[j]['low'] for j in range(i - window, i + window + 1) if j != i)

        if is_max:
            extremum_points.append({'time': data[i]['time'], 'value': data[i]['high'], 'type': 'max'})
        elif is_min:
            extremum_points.append({'time': data[i]['time'], 'value': data[i]['low'], 'type': 'min'})
    return extremum_points

def fetch_and_emit_data(symbol, interval):
    global current_data
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100'
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            formatted_data = [{
                'time': d[0] / 1000,
                'open': float(d[1]),
                'high': float(d[2]),
                'low': float(d[3]),
                'close': float(d[4]),
            } for d in data]

            extremum_points = find_extremum(formatted_data)

            with data_lock:
                current_data = []
                for i in range(len(formatted_data)):
                    current_data.append(formatted_data[i])
                    socketio.emit('update_data', {'data': formatted_data[i], 'extremum_points': extremum_points})
                    time.sleep(3)

        except requests.exceptions.RequestException as e:
            print(f'Error fetching data: {e}')
            time.sleep(10)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    
    thread = threading.Thread(target=fetch_and_emit_data, args=(symbol, interval))
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    with open('crypto_chart_app/index.html', 'r') as f:
        return f.read()

@app.route('/klines')
def get_klines():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval')
    limit = 100

    if not symbol or not interval:
        return jsonify({'error': 'Missing symbol or interval'}), 400

    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        formatted_data = [{
            'time': d[0] / 1000,
            'open': float(d[1]),
            'high': float(d[2]),
            'low': float(d[3]),
            'close': float(d[4]),
        } for d in data]

        return jsonify(formatted_data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching data: {e}'}), 500

@app.route('/chart')
def chart():
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1h')

    # Fetch data from Binance API (using /klines route)
    try:
        response = requests.get(f'http://localhost:5000/klines?symbol={symbol}&interval={interval}')
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return f'Error fetching data: {e}', 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
