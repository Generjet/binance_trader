import os
import schedule
import time


def trade5m():
	os.system('/home/tamiserver/.rbenv/shims/ruby trade5min.rb')
	print("5m trade RUBY run")

def analyze5m():
	os.system('/home/tamiserver/miniconda3/bin/python analyze5m.py')
	print('5m ANALYZE python RUN')

schedule.every(5).minutes.do(analyze5m)
schedule.every(7).minutes.do(trade5m)

while True:
	schedule.run_pending()
	time.sleep(1)