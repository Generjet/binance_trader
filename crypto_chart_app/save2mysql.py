from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
from sqlalchemy import text # Import text
from sqlalchemy import inspect
import numpy as np
import pandas as pd
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Tamir4578@localhost/portalblog_dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class AnalyzedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(255))
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.Float)
    resistance = db.Column(db.Float)
    support = db.Column(db.Float)
    macd = db.Column(db.Float)
    macd_signal = db.Column(db.Float)
    macd_hist = db.Column(db.Float)
    rsi = db.Column(db.Float)
    ema = db.Column(db.Float)
    stochastic_D = db.Column(db.Float)
    stochastic_K = db.Column(db.Float)
    near_support = db.Column(db.Float)
    near_resistance = db.Column(db.Float)
    engulfing = db.Column(db.String(255))
    doji = db.Column(db.String(255))
    reversal = db.Column(db.String(255))
    macd_trade = db.Column(db.String(255))
    rsi_trade = db.Column(db.String(255))
    stochastic_trade = db.Column(db.String(255))
    channel_trade = db.Column(db.String(255))
    bb_upper = db.Column(db.Float)
    bb_middle = db.Column(db.Float)
    bb_lower = db.Column(db.Float)
    bb_trend = db.Column(db.String(255))
    bb_signal = db.Column(db.String(255))
    near_bb_support = db.Column(db.Float)
    near_bb_resistance = db.Column(db.Float)

def create_database_if_not_exists():
    # Connect to MySQL server without specifying a database
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Tamir4578'
    )
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS portalblog_dev")
    cursor.close()
    connection.close()

    # Create tables if they do not exist
    with app.app_context():
        db.create_all()

def alter_table_add_columns():
    with app.app_context():
        inspector = inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('analyzed_data')]
        if 'macd_trade' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN macd_trade VARCHAR(255) DEFAULT NULL"))
        if 'rsi_trade' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN rsi_trade VARCHAR(255) DEFAULT NULL"))
        if 'stochastic_trade' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN stochastic_trade VARCHAR(255) DEFAULT NULL"))
        if 'channel_trade' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN channel_trade VARCHAR(255) DEFAULT NULL"))
        if 'macd_hist' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN macd_hist FLOAT DEFAULT NULL"))
        if 'macd_signal' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN macd_signal FLOAT DEFAULT NULL"))
        if 'near_support' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN near_support FLOAT DEFAULT NULL"))
        if 'near_resistance' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN near_resistance FLOAT DEFAULT NULL"))
        if 'engulfing' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN engulfing VARCHAR(255) DEFAULT NULL"))
        if 'doji' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN doji VARCHAR(255) DEFAULT NULL"))
        if 'reversal' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN reversal VARCHAR(255) DEFAULT NULL"))
        if 'bb_upper' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN bb_upper FLOAT DEFAULT NULL"))
        if 'bb_middle' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN bb_middle FLOAT DEFAULT NULL"))
        if 'bb_lower' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN bb_lower FLOAT DEFAULT NULL"))
        if 'bb_trend' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN bb_trend VARCHAR(255) DEFAULT NULL"))
        if 'bb_signal' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN bb_signal VARCHAR(255) DEFAULT NULL"))
        if 'near_bb_support' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN near_bb_support FLOAT DEFAULT NULL"))
        if 'near_bb_resistance' not in columns:
            db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN near_bb_resistance FLOAT DEFAULT NULL"))
        db.session.commit()
        print("AnalyzedData table altered to add Bollinger Bands columns.")
        print("AnalyzedData table altered to add near_support and near_resistance columns.")
# ========= Update row ================
def update_db(row):
    with app.app_context():
        # Replace NaN values with None
        row = {key: (None if pd.isna(value) else value) for key, value in row.items()}
        
        # Check if a record with the same 'time' exists
        existing_record = AnalyzedData.query.filter_by(time=row['time']).first()
        
        if existing_record:
            # Update existing record
            existing_record.open = row['open']
            existing_record.high = row['high']
            existing_record.low = row['low']
            existing_record.close = row['close']
            existing_record.volume = row['volume']
            existing_record.resistance = row.get('resistance', None)
            existing_record.support = row.get('support', None)
            existing_record.macd = row.get('macd', None)
            existing_record.macd_signal = row.get('macd_signal', None)
            existing_record.macd_hist = row.get('macd_hist', None)
            existing_record.rsi = row.get('rsi', None)
            existing_record.ema = row.get('ema', None)
            existing_record.stochastic_D = row.get('stochastic-D', None)
            existing_record.stochastic_K = row.get('stochastic-K', None)
            existing_record.near_support = row.get('near_support', None)
            existing_record.near_resistance = row.get('near_resistance', None)
            existing_record.engulfing = row.get('engulfing', None)
            existing_record.doji = row.get('doji', None)
            existing_record.reversal = row.get('reversal', None)
            existing_record.macd_trade = row.get('macd_trade', 'wait')
            existing_record.rsi_trade = row.get('rsi_trade', 'wait')
            existing_record.stochastic_trade = row.get('stochastic_trade', 'wait')
            existing_record.channel_trade = row.get('channel_trade', 'wait')
            existing_record.bb_upper = row.get('bb_upper', None)
            existing_record.bb_middle = row.get('bb_middle', None)
            existing_record.bb_lower = row.get('bb_lower', None)
            existing_record.bb_trend = row.get('bb_trend', 'wait')
            existing_record.bb_signal = row.get('bb_signal', 'wait')
            existing_record.near_bb_support = row.get('near_bb_support', None)
            existing_record.near_bb_resistance = row.get('near_bb_resistance', None)
            print("Data updated for time:", row['time'])
        else:
            # Create new record
            analyzed_data = AnalyzedData(
                time=row['time'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume'],
                resistance=row.get('resistance', None),
                support=row.get('support', None),
                macd=row.get('macd', None),
                macd_signal=row.get('macd_signal', None),
                macd_hist=row.get('macd_hist', None),
                rsi=row.get('rsi', None),
                ema=row.get('ema', None),
                stochastic_D=row.get('stochastic-D', None),
                stochastic_K=row.get('stochastic-K', None),
                near_support=row.get('near_support', None),
                near_resistance=row.get('near_resistance', None),
                engulfing=row.get('engulfing', None),
                doji=row.get('doji', None),
                reversal=row.get('reversal', None),
                macd_trade=row.get('macd_trade', 'wait'),
                rsi_trade=row.get('rsi_trade', 'wait'),
                stochastic_trade=row.get('stochastic_trade', 'wait'),
                channel_trade=row.get('channel_trade', 'wait'),
                bb_upper = row.get('bb_upper', None),
                bb_middle = row.get('bb_middle', None),
                bb_lower = row.get('bb_lower', None),
                bb_trend = row.get('bb_trend', 'wait'),
                bb_signal = row.get('bb_signal', 'wait'),
                near_bb_support=row.get('near_bb_support', None),
                near_bb_resistance=row.get('near_bb_resistance', None)
            )
            db.session.add(analyzed_data)
            print("Data saved for time:", row['time'])
        
        db.session.commit()
# ========= MAIN ================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'table':
        alter_table_add_columns() # Call alter_table_add_columns instead
        print("Database table alteration attempted.")
    elif len(sys.argv) > 1 and sys.argv[1] == 'data':
        # Create database if it does not exist
        create_database_if_not_exists()
    else:
        create_database_if_not_exists() # Call create_database_if_not_exists for other cases
        print("Run with 'python save2mysql.py table' to update database tables.")