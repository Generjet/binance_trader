from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import plotly.graph_objects as go
from save2mysql import db, AnalyzedData

app = Flask(__name__, static_folder='static')
CORS(app)

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
        table_html = df.to_html(classes='data', index=False, border=0)

        return render_template('index.html', chart_html=chart_html, table_data=table_html)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
