import os
import schedule
import time

# RUBY
def trade5m():
	os.system('ruby trade5min.rb')
	print("5m trade RUBY run")

def trade15m():
	os.system('ruby trade15min.rb')
	print("15m trade RUBY run")

def trade30m():
	os.system('ruby trade30m.rb')
	print("30m trade RUBY run")

def trade1h():
	os.system('ruby trade1h.rb')
	print("1h trade RUBY run")

def trade2h():
	os.system('ruby trade2h.rb')
	print("2h trade RUBY run")

def trade4h():
	os.system('ruby trade4h.rb')
	print("4h trade RUBY run")

def trade8h():
	os.system('ruby trade8h.rb')
	print("8h trade RUBY run")

def trade1d():
	os.system('ruby trade1d.rb')
	print("1d trade RUBY run")
# PYTHON
def analyze5m():
	os.system('python analyze5m.py')
	print('5m ANALYZE python RUN')

def analyze15m():
	os.system('python analyze15m.py')
	print('15m ANALYZE python RUN')

def analyze30m():
	os.system('python analyze30m.py')
	print('30m ANALYZE python RUN')

def analyze1h():
	os.system('python analyze1h.py')
	print('1h ANALYZE python RUN')

def analyze4h():
	os.system('python analyze4h.py')
	print('4h ANALYZE python RUN')

def analyze8h():
	os.system('python analyze8h.py')
	print('8h ANALYZE python RUN')

def analyze1d():
	os.system('python analyze1d.py')
	print('1d ANALYZE python RUN')
# 30m
schedule.every(5).minutes.do(analyze30m)
schedule.every(7).minutes.do(trade30m)
# 4h
schedule.every(4).hours.do(analyze4h)
schedule.every(4).hours.at("02:15").do(trade4h)
# Run jobs every 5th hour, 20 minutes and 30 seconds in.
# If current time is 02:00, first execution is at 06:20:30
# schedule.every(5).hours.at("20:30").do(job)

while True:
	schedule.run_pending()
	time.sleep(1)