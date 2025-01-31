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
    rsi = db.Column(db.Float)
    ema = db.Column(db.Float)
    stochastic_D = db.Column(db.Float)
    stochastic_K = db.Column(db.Float)
    near_support = db.Column(db.Boolean)
    near_resistance = db.Column(db.Boolean)

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

    near_support = db.Column(db.Boolean)
    near_resistance = db.Column(db.Boolean)

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
        db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN near_support BOOLEAN DEFAULT NULL"))
        db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN near_resistance BOOLEAN DEFAULT NULL"))
        db.session.commit()
        print("AnalyzedData table altered to add near_support and near_resistance columns.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'table':
        alter_table_add_columns() # Call alter_table_add_columns instead
        print("Database table alteration attempted.")
    else:
        create_database_if_not_exists() # Call create_database_if_not_exists for other cases
        print("Run with 'python save2mysql.py table' to update database tables.")
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
            stochastic_K=row.get('stochastic-K', None),
            near_support=row.get('near_support', None),       # Add near_support
            near_resistance=row.get('near_resistance', None) # Add near_resistance
        )
        db.session.add(analyzed_data)
        db.session.commit()
        print("Data saved for time:", row['time'])
