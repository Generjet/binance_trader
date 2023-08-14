require 'csv'
require 'binance'
# require 'mysql2'
require 'sqlite3'
require 'active_record'
require 'date'

# ==== GET arguments from command line ====
period = ARGV[0]
puts "available period parameters are: 1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M"
puts 'GOT PERIOD VARIABLE from COMMAND LINE: => '+period

# === ACTIVE RECORD connection =====
# now = DateTime.now.strftime "%Y-%m-%d  %H:%M:%S"
now = DateTime.now
# period = '15min'
# ===== establish connection ======
    ActiveRecord::Base.establish_connection( 
        :adapter => "sqlite3",
        :host => "localhost",
        :database => "../rails/trader/db/development.sqlite3"
       )
# =====================

# 1. ============= Create a new client instance. ==============
# ==== turshiltiih =====
client = Binance::Spot.new(base_url: 'https://testnet.binance.vision')
puts client.time
# ==== jinhene =======
# client = Binance::Spot.new(key: ENV["bot_api_key"], secret: ENV["bot_api_secret"])
# Send a request to query BTCUSDT ticker
current_price = client.ticker_24hr(symbol: 'ETHUSDT')
lastPrice = current_price[:lastPrice].to_f

puts " #========== BINANCE API-> PAUSED for TEST: after test uncomment lines above ========== !"
# lastPrice = 1835.05
puts "LAST PRICE: "+current_price[:lastPrice]
# Send a request to get account information
# my_account = client.account


# 2. ================== Read Signals ======================
# === from SQL =====
class TradeSignal < ActiveRecord::Base
    self.table_name = 'trade_signals'
end

lastSignal = TradeSignal.where(period: period).last

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

# ==== check Buy or Sell condition from signals ====
# === BUY signals ===
buy_zone = true if lastSignal.buy_zone > lastPrice
buy_stoch = true if (lastSignal.k < 30) && (lastSignal.d < 30) && (lastSignal.k < lastSignal.d)
buy_rsi = true if (lastSignal.rsi < 50)
buy_macd = true if (lastSignal.macd < -15)
# === SELL signals ===
sell_zone = true if lastSignal.sell_zone < lastPrice
sell_stoch = true if (lastSignal.k > 70) && (lastSignal.d > 70) && (lastSignal.k > lastSignal.d)
sell_rsi = true if (lastSignal.rsi > 65)
sell_macd = true if (lastSignal.macd > 20)

puts "Now Price:"+lastPrice.to_s+" BuyZone: "+lastSignal.buy_zone.to_s + " SellZone: "+lastSignal.sell_zone.to_s

if buy_zone && buy_stoch && buy_rsi
    puts "NowPrice:"+lastPrice.to_s+" < BuyZone:"+lastSignal.buy_zone.to_s + " ==> U can buy"
elsif sell_zone && sell_stoch && sell_rsi
    puts "NowPrice:"+lastPrice.to_s+" > SellZone:"+lastSignal.sell_zone.to_s + " ==> U can SELL"
else
    puts "Now Price:"+lastPrice.to_s+" BuyZone: "+lastSignal.buy_zone.to_s + " SellZone: "+lastSignal.sell_zone.to_s + " ==> WAIT"
end

# 3. ================== Read Orders ================
class Orders < ActiveRecord::Base
    self.table_name = 'orders'
        # has_many :table_relationship
end

# ========== query not SOLD trade orders by activerecord =========
# === SELL ORDER ===
def sell(order,now,lastPrice, lastSignal)
    order.sell_date = now
    order.sell_amount = order.buy_amount
    order.sell_price = lastPrice
    order.sell_signal_id = lastSignal.id
    order.save
end

# === BUY ORDER ====
# :profit, :channel_id,:trade_type,:period, :buy_signal_id, :sell_signal_id, :buy_amount, :buy_price, :buy_date, :sell_amount, :sell_price, :sell_date
def buy(now,lastPrice, lastSignal, buy_amount, period)
    order = Order.new
    order.buy_date = now
    order.buy_amount = buy_amount
    order.buy_price = lastPrice
    order.buy_signal_id = lastSignal.id
    order.period = period
    order.save
end

buy_amount = 0.2
# order = Orders.where(sell_amount: [nil, "", 0.0]).last
# 5min, 15min ... 4h гэх мэт цагаар фильтерлэж, зарагдсан утга байхгүйг нь ялгаж авна.
order = Orders.where(period: period).where(sell_amount: [nil, 0.0, ""]).last

# abort "LAST OPEN ORDER "+order.buy_date.to_s

# order.sell_amount нь activerecord-ийн float учир нэг бол nil, нэг бол 0.0 байна
if order.sell_amount.blank? || order.sell_amount <= 0.0   # Хэрэв buy=done, sell=NOT_DONE_YET буюу зарагдаагүй бол
    sell(order,now,lastPrice, lastSignal)
    puts "UNFINISHED TRADE EXISTS: BUY=yes, SELL=nil"
else
    buy(now,lastPrice, lastSignal, buy_amount, period) # Хэрэв buy=done, sell=done бол шинээр АВАХ захиалга өгч болно.
    puts "PREVIOUS TRADE FINISHED: you can create new one"
end





puts "======== ORDER ========"
puts "order.buy_date:"+ order.buy_date.to_s + "order.sell_date:"+order.sell_date.to_s
# abort "DEBUG =====> DONE"



# 4. ============= Place an order ========================
# response = client.new_order(symbol: 'ETHUSDT', side: 'SELL', price: 1945, quantity: 0.0294, type: 'LIMIT', timeInForce: 'GTC')

# 5. ============== Update or Insert into Orders =========
# # === insert ===
# order = Orders.new
# order.buy_signal = ARGV[0]
# order.buy_time = ARGV[1]
# order.buy_order = ARGV[2]
# order.buy_amount = ARGV[3]
# order.buy_price = ARGV[4]
# order.currency = ARGV[5]
# order.save