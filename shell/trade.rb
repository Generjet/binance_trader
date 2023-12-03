require 'csv'
require 'binance'
# require 'mysql2'
require 'sqlite3'
require 'active_record'
require 'date'

# ==== GET arguments from command line ====
period = ARGV[0]
# strategy: 1.rocket -no resistance, only SIGNALS 2. channel - between support&resistance only 3. mixed - both SIGNALS&Channels
strategy = ARGV[1]
puts "available period parameters are: 1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M"
puts 'GOT PERIOD VARIABLE from COMMAND LINE: => '+period
puts 'GOT STRATEGY: '+strategy

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

# puts "DEBUG: Now Price:"+lastPrice.to_s+" BuyZone: "+lastSignal.buy_zone.to_s + " SellZone: "+lastSignal.sell_zone.to_s

# 3. ================== Read Orders ================
class Orders < ActiveRecord::Base
    self.table_name = 'orders'
        # has_many :table_relationship
end

# ========== query not SOLD trade orders by activerecord =========
# === SELL ORDER ===
def sell(order,now,lastPrice, lastSignal, strategy)
    order.sell_date = now
    order.sell_amount = order.buy_amount
    order.sell_price = lastPrice
    order.sell_signal_id = lastSignal.id
    order.profit  = order.sell_price - order.buy_price
    # === set order -> trade_type ====
    order.trade_type = strategy
    order.save
end

# === BUY ORDER ====
# :profit, :channel_id,:trade_type,:period, :buy_signal_id, :sell_signal_id, :buy_amount, :buy_price, :buy_date, :sell_amount, :sell_price, :sell_date
def buy(now,lastPrice, lastSignal, buy_amount, period, strategy)
    order = Orders.new
    order.buy_date = now
    order.buy_amount = buy_amount
    order.buy_price = lastPrice
    order.buy_signal_id = lastSignal.id
    order.period = period
    # === set order -> trade_type ====
    order.trade_type = strategy
    order.save
end

buy_amount = 0.2
# order = Orders.where(sell_amount: [nil, "", 0.0]).last
# 5min, 15min ... 4h гэх мэт цагаар фильтерлэж, зарагдсан утга байхгүйг нь ялгаж авна.
# order = Orders.where(period: period).where(sell_amount: [nil, 0.0]).last
# order = Orders.where(period: period).last
order = Orders.where(period: period).where(trade_type: strategy).last
# ====== previous order finished or not, check it ======
if order 
    puts "STRATGEY ORDER =========> :  buy_date: "+order.buy_date.to_s + " sell_date: "+ order.sell_date.to_s + " sell_amount: "+ order.sell_amount.to_s
    if order.buy_amount != nil && order.sell_amount != nil
        u_can_buy = true
        u_can_sell = false
    elsif order.buy_amount != nil && order.sell_amount.nil? && lastPrice > (order.buy_price + 5.0)
        u_can_buy = false
        u_can_sell = true
    end
else
    u_can_buy = true
    u_can_sell = false
end

puts "BUY or SELL  " + order.buy_amount.to_s if order
# ==== decide to trade based on decision of previous order finished or not and signals =====

# ================= STRATEGY: ROCKET =======================
if strategy == 'rocket'
    puts 'ROCKET STRATEGY'
    # === SELL signals for ROCKET strategy can be customized ===
    sell_zone = true if lastSignal.sell_zone < lastPrice
    sell_stoch = true if (lastSignal.k > 85) && (lastSignal.d > 85) && (lastSignal.k > lastSignal.d)
    sell_rsi = true if (lastSignal.rsi > 80)
    sell_macd = true if (lastSignal.macd > 20)
    if buy_zone && buy_stoch && buy_rsi && u_can_buy == true
        puts "NowPrice:"+lastPrice.to_s+" < BuyZone:"+lastSignal.buy_zone.to_s + " ==> U can buy"
        buy(now,lastPrice, lastSignal, buy_amount, period, strategy) # Хэрэв buy=done, sell=done бол шинээр АВАХ захиалга өгч болно.
        lastSignal.bot_signal = 'buy'
    elsif sell_stoch && sell_rsi && u_can_sell == true
        puts "NowPrice:"+lastPrice.to_s+" > SellZone:"+lastSignal.sell_zone.to_s + " ==> U can SELL"
        lastSignal.bot_signal = 'sell'
        sell(order,now,lastPrice, lastSignal, strategy)
    else
        lastSignal.bot_signal = 'wait'
        puts "Now Price:"+lastPrice.to_s+" BuyZone: "+lastSignal.buy_zone.to_s + " SellZone: "+lastSignal.sell_zone.to_s + " ==> WAIT"
    end
end
# ================= STRATEGY: CHANNEL ======================
if strategy == 'channel'
    puts 'CHANNEL STRATEGY'
    if buy_zone && u_can_buy == true
        puts "NowPrice:"+lastPrice.to_s+" < BuyZone:"+lastSignal.buy_zone.to_s + " ==> U can buy"
        buy(now,lastPrice, lastSignal, buy_amount, period, strategy) # Хэрэв buy=done, sell=done бол шинээр АВАХ захиалга өгч болно.
        lastSignal.bot_signal = 'buy'
    elsif sell_zone && u_can_sell == true
        puts "NowPrice:"+lastPrice.to_s+" > SellZone:"+lastSignal.sell_zone.to_s + " ==> U can SELL"
        lastSignal.bot_signal = 'sell'
        sell(order,now,lastPrice, lastSignal, strategy)
    else
        lastSignal.bot_signal = 'wait'
        puts "Now Price:"+lastPrice.to_s+" BuyZone: "+lastSignal.buy_zone.to_s + " SellZone: "+lastSignal.sell_zone.to_s + " ==> WAIT"
    end
end

# ================= STRATEGY: MIXED =========================
if strategy.nil? || strategy == 'mixed'
    puts 'MIXED STRATEGY'
    if buy_zone && buy_stoch && buy_rsi && u_can_buy == true
        puts "NowPrice:"+lastPrice.to_s+" < BuyZone:"+lastSignal.buy_zone.to_s + " ==> U can buy"
        buy(now,lastPrice, lastSignal, buy_amount, period, strategy) # Хэрэв buy=done, sell=done бол шинээр АВАХ захиалга өгч болно.
        lastSignal.bot_signal = 'buy'
    elsif sell_zone && sell_stoch && sell_rsi && u_can_sell == true
        puts "NowPrice:"+lastPrice.to_s+" > SellZone:"+lastSignal.sell_zone.to_s + " ==> U can SELL"
        lastSignal.bot_signal = 'sell'
        sell(order,now,lastPrice, lastSignal, strategy)
    else
        lastSignal.bot_signal = 'wait'
        puts "Now Price:"+lastPrice.to_s+" BuyZone: "+lastSignal.buy_zone.to_s + " SellZone: "+lastSignal.sell_zone.to_s + " ==> WAIT"
    end
end

# === saving lastSignal.bot_signal value for further analysis
lastSignal.save

puts "======== ORDER DONE========"