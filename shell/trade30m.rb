require 'csv'
require 'binance'
# require 'mysql2'
require 'sqlite3'
require 'active_record'
require 'date'
require 'binance-ruby'
period = '30m'
puts "======== RUBY ============ #{period} ======> :"
# ========== CRONJOB test ===========
# File.open('rubyAutomationResult.txt',"a") { |f| f.write "Ruby Automation is done at #{Time.now} successfully \n" }

# === ACTIVE RECORD connection =====
# now = DateTime.now.strftime "%Y-%m-%d  %H:%M:%S"
now = DateTime.now
# ===== establish connection ======
    ActiveRecord::Base.establish_connection( 
        :adapter => "sqlite3",
        :host => "localhost",
        :database => "../rails/trader/db/development.sqlite3"
       )
# =====================

# 1. ============= Create a new client instance. ==============
# ==== turshiltiih =====
# client = Binance::Spot.new(base_url: 'https://testnet.binance.vision')
# puts client.time
# ==== jinhene =======
client = Binance::Spot.new(key: ENV["API_KEY"], secret: ENV["API_SECRET"])
# Send a request to query BTCUSDT ticker
current_price = client.ticker_24hr(symbol: 'ETHUSDT')
lastPrice = current_price[:lastPrice].to_f
puts lastPrice
# Send a request to get account information
my_account = client.account
# ===== Available USDT for BUY trade ==========
usdt = Hash.new
my_account[:balances].each do |coin|
    if coin[:asset] == 'USDT'
        usdt = coin
    end
end
puts usdt

# ========== Calculation of amount for BUY trade =========
# 5m, 15m,30m,1h,2h,4h,8h,1d гэсэн 8 last row л байна. Үүнээс өөрөөр хийж болохгүй одоохондоо, утсгаж болохгүй, зөвхөн status l солино
class TradeStatus < ActiveRecord::Base
    self.table_name = 'trade_statuses'
end
possible_trades = TradeStatus.where(trade_status: 'close').last(8).count
balance = usdt[:free].to_f
buy_amount = balance/possible_trades # this is expressed in USDT
# ==== Calculate quantity for Buy trade ======
quantity = buy_amount/lastPrice
puts " ***** POSSIBLE TRADES => #{possible_trades} and BALANCE = #{balance} and BUY_AMOUNT => #{buy_amount} USDT -> #{quantity} ETH "
# 2. ================== Read Signals ======================
# === from SQL =====
class TradeSignal < ActiveRecord::Base
    self.table_name = 'trade_signals'
end

lastSignal = TradeSignal.where(period: period).last
if lastSignal
    puts "TradeSignal.where(period: #{period}) ===> "
    puts "DATE: "+ lastSignal.date.to_s+" PERIOD: "+lastSignal.period.to_s
else
    abort "No LAST SIGNALS, quit"
end

puts "TradeSignal.where(period: #{period}) ===> "
puts "DATE: "+ lastSignal.date.to_s+" PERIOD: "+lastSignal.period.to_s
# abort "TEST DONE! "

# ==== check date for last signals =====
# ==== time comparison ====
last1hour = (now - 1.hours).strftime "%Y-%m-%d  %H:%M:%S"
last5mins = (now - 7.minutes).strftime "%Y-%m-%d  %H:%M:%S"
now = DateTime.now.strftime "%Y-%m-%d  %H:%M:%S"

withinRange = lastSignal.date.between?(last5mins, now)
puts "WITHIN RANGE -> "+withinRange.to_s
puts last5mins.to_s+" = Last hour "
puts now.to_s + "= now"
puts lastSignal.date.to_s + " = lastSignal.date "

unless withinRange
    abort "Signal Hour Differs: ===> exit"
end

# 3. ================== Read Orders ================
class Orders < ActiveRecord::Base
    self.table_name = 'orders'
        # has_many :table_relationship
end

# === SELL ORDER ===
def sell(order,now,lastPrice, lastSignal, period,coin_quantity)
    sell_trade = client.new_order(symbol: 'ETHUSDT', side: 'SELL', quantity: coin_quantity, type: 'MARKET')
    order.sell_date = now
    order.sell_amount = order.buy_amount
    order.sell_price = lastPrice
    order.sell_signal_id = lastSignal.id
    order.save
    # === update Trade_status table ====
    trade_status = TradeStatus.where(period: period).last
    trade_status.trade_status = 'close'
    trade_status.save
end
# === BUY ORDER ====
# :profit, :channel_id,:trade_type,:period, :buy_signal_id, :sell_signal_id, :buy_amount, :buy_price, :buy_date, :sell_amount, :sell_price, :sell_date
def buy(now,lastPrice, lastSignal, buy_amount, period,coin_quantity)
    buy_trade = client.new_order(symbol: 'ETHUSDT', side: 'BUY', quantity: coin_quantity, type: 'MARKET')
    order = Orders.new
    order.buy_date = now
    order.buy_amount = buy_amount
    order.buy_price = lastPrice
    order.buy_signal_id = lastSignal.id
    order.period = period
    order.save
    # === update Trade_status table ====
    puts "===== Trade Status period => #{period}"
    trade_status = TradeStatus.where(period: period).last
    trade_status.trade_status = 'open'
    trade_status.save
end

# order = Orders.where(period: period).where(sell_amount: [nil, 0.0, ""]).last
order = Orders.where(period: period).last

# order_not_sold = true if (order.sell_amount.blank? || order.sell_amount <= 0.0 || order.sell_amount.nil?)
if order && (order.sell_amount.blank? || order.sell_amount <= 0.0 || order.sell_amount.nil?)
    order_not_sold = true
else
    order_not_sold = false
end

# ===== NEW METHOD for TRADE DECISION using only Python signals ============
puts "LAST SIGNAL ============ > #{lastSignal.bot_signal}"
if lastSignal.bot_signal == "buy"
    puts "NowPrice:"+lastPrice.to_s+" < BuyZone:"+lastSignal.buy_zone.to_s + " ==> U can buy"
    if order_not_sold == false
        puts "PREVIOUS TRADE FINISHED: you can buy new one"
        buy(now,lastPrice, lastSignal, buy_amount, period,quantity) # Хэрэв buy=done, sell=done бол шинээр АВАХ захиалга өгч болно.
    end
elsif lastSignal.bot_signal == "sell"
    puts "NowPrice:"+lastPrice.to_s+" > SellZone:"+lastSignal.sell_zone.to_s + " ==> U can SELL"
    if order_not_sold == true
        puts "UNFINISHED TRADE EXISTS: BUY=yes, SELL=nil"
        sell(order,now,lastPrice, lastSignal,period,quantity)
    end
else
    puts "Now Price:"+lastPrice.to_s+" BuyZone: "+lastSignal.buy_zone.to_s + " SellZone: "+lastSignal.sell_zone.to_s + " ==> WAIT"
    abort "NO Buy/Sell signal, only Wait signal => ABORT"
end

abort "DEBUG =====> DONE"

# 4. ============= Place an order ========================
# response = client.new_orde r(symbol: 'ETHUSDT', side: 'SELL', price: 1945, quantity: 0.0294, type: 'LIMIT', timeInForce: 'GTC')
# puts "======== ORDER ========"
# puts "order.buy_date:"+ order.buy_date.to_s + "order.sell_date:"+order.sell_date.to_s if order