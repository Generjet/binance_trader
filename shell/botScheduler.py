import os
import schedule
import time


def trade5m():
	# os.system('C:\Ruby32-x64\bin\ruby.exe trade5min.rb')
	os.system('ruby trade5min.rb')
	print("5m trade RUBY run")

def analyze5m():
	# os.system('C:\Users\GoodLuck\miniconda3\python.exe analyze5m.py')
	os.system('python analyze5m.py')
	print('5m ANALYZE python RUN')

schedule.every(5).minutes.do(analyze5m)
schedule.every(7).minutes.do(trade5m)

while True:
	schedule.run_pending()
	time.sleep(1)