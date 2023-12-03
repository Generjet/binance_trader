1. Prerequisites
conda create -n binanceBot python=3.7.0
conda activate binanceBot
conda install pandas==1.1.1
conda install ta
conda install matplotlib

2. Ajilluulah gol hesguud
# 1. /shell/analyze.py <period> ogch ajilluulna, => rails/db/development.sqlite3 ruu trade_signals table ruu resultiig bichne
RUN:
python analyze.py 30m

# 2. /shell/trade.rb <period> <strategy> ogch ajilluulna
<strategy> n rocket|mixed|channel
RUN:
ruby trade.rb 30m channel

# 3. /shell/botScheduler.py
RUN:
python botScheduler.py

