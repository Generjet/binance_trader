from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='static')
CORS(app)

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
    app.run(debug=True, host='0.0.0.0')
