from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import numpy as np
import pandas as pd

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
    rsi = db.Column(db.Float)
    ema = db.Column(db.Float)
    stochastic_D = db.Column(db.Float)
    stochastic_K = db.Column(db.Float)

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

def update_db(row):
    with app.app_context():
        # Replace NaN values with None
        row = {key: (None if pd.isna(value) else value) for key, value in row.items()}
        
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
            rsi=row.get('rsi', None),
            ema=row.get('ema', None),
            stochastic_D=row.get('stochastic-D', None),
            stochastic_K=row.get('stochastic-K', None)
        )
        db.session.add(analyzed_data)
        db.session.commit()
        print("Data saved for time:", row['time'])
