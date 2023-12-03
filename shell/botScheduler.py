import os
import schedule
import time

trade_periods = ['5m','15m','30m','1h','4h','8h','1d','3d','1w']

# =============== ANALYZE ===================
# 5 M
def analyze5m():
	os.system('python analyze.py 5m')
	print('5m ANALYZE python RUN')

# 15 M
def analyze15m():
	os.system('python analyze.py 15m')
	print('15m ANALYZE python RUN')

# 30 M
def analyze30m():
	os.system('python analyze.py 30m')
	print('30m ANALYZE python RUN')

# 1 H
def analyze1h():
	os.system('python analyze.py 1h')
	print('1h ANALYZE python RUN')

# 4 H
def analyze4h():
	os.system('python analyze.py 4h')
	print('4h ANALYZE python RUN')

# 8 H
def analyze8h():
	os.system('python analyze.py 8h')
	print('8h ANALYZE python RUN')

# 1 D
def analyze1d():
	os.system('python analyze.py 1d')
	print('1d ANALYZE python RUN')

# 3 D
def analyze3d():
	os.system('python analyze.py 3d')
	print('3d ANALYZE python RUN')

# 1 W
def analyze1w():
	os.system('python analyze.py 1w')
	print('1w ANALYZE python RUN')

# =============== TRADE ======================
# 5 M
def trade5m():
	os.system('ruby trade.rb 5m mixed')
	print("5m trade RUBY run")

# 15 M
def trade15m():
	os.system('ruby trade.rb 15m mixed')
	print("15m trade RUBY run")

# 30 M
def trade30m():
	os.system('ruby trade.rb 30m mixed')
	print("30m trade RUBY run")

# 1 H
def trade1h():
	os.system('ruby trade.rb 1h mixed')
	print("1h trade RUBY run")

# 4 H
def trade4h():
	os.system('ruby trade.rb 4h mixed')
	print("4h trade RUBY run")

# 8 H
def trade8h():
	os.system('ruby trade.rb 8h mixed')
	print("8h trade RUBY run")

# 1 D
def trade1d():
	os.system('ruby trade.rb 1d mixed')
	print("1d trade RUBY run")

# 3 D
def trade3d():
	os.system('ruby trade.rb 3d mixed')
	print("3d trade RUBY run")

# 1 W
def trade5m():
	os.system('ruby trade.rb 1w mixed')
	print("1w trade RUBY run")

# 5m
schedule.every(5).minutes.do(analyze5m)
schedule.every(7).minutes.do(trade5m)
# 15m
schedule.every(15).minutes.do(analyze15m)
schedule.every(17).minutes.do(trade15m)
# 30m
schedule.every(30).minutes.do(analyze30m)
schedule.every(32).minutes.do(trade30m)
# 1h
schedule.every(60).minutes.do(analyze1h)
schedule.every(62).minutes.do(trade1h)
# 4h
schedule.every(4).hours.at(":4").do(analyze4h)
schedule.every(4).hours.at(":6").do(trade4h)
# schedule.every(240).minutes.do(analyze4h)
# schedule.every(242).minutes.do(trade4h)

# 8h
# Run job every hour at the 42nd minute
schedule.every(8).hours.at(":9").do(analyze8h)
schedule.every(8).hours.at(":11").do(trade8h)
# schedule.every(320).minutes.do(analyze8h)
# schedule.every(322).minutes.do(trade8h)

# 1d
# Run job every day at specific HH:MM and next HH:MM:SS
schedule.every().day.at("01:19").do(analyze1d)
schedule.every().day.at("01:21").do(trade1d)
# schedule.every(320).minutes.do(analyze8h)
# schedule.every(322).minutes.do(trade8h)

# 3d
# Run job every day at specific HH:MM and next HH:MM:SS
schedule.every(3).days.at("02:19").do(analyze1d)
schedule.every(3).days.at("02:21").do(trade1d)

# 1w
schedule.every(3).weeks.at("03:19").do(analyze1w)
schedule.every(3).weeks.at("03:21").do(trade1w)

while True:
	schedule.run_pending()
	time.sleep(1)