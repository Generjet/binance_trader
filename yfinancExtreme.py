import yfinance as yf
data = yf.download(tickers='BTC-USD', period='max', interval='1d')
print(data)