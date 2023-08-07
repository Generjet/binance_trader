require 'csv'
require 'binance'
# require 'mysql2'
require 'sqlite3'
require 'active_record'
require 'date'

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
client = Binance::Spot.new(key: ENV["bot_api_key"], secret: ENV["bot_api_secret"])
# Send a request to query BTCUSDT ticker
current_price = client.ticker_24hr(symbol: 'ETHUSDT')
lastPrice = current_price[:lastPrice].to_f
puts lastPrice
# Send a request to get account information
my_account = client.account


# 2. ================== Read Signals ======================
# file = CSV.read("signals.csv")
# file = CSV.parse(File.read("orders.csv"), headers: true)
# CSV.foreach('signals.csv', :headers => true) do |row|
#     puts row['support']
#     puts row['time_period']
# end

# === from SQL =====
class TradeSignal < ActiveRecord::Base
    self.table_name = 'trade_signals'
end

signals = TradeSignal.all
lastSignal = TradeSignal.last
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

# === Python reference ===
# long['Sell'] = np.where( (long['%K'].between(75,100)) & (long['%D'].between(75,100)) & (long['%K'] > long['%D'] ) & (long['rsi'] > 65) & ( long['Close'] > long['sell_zone'] ) & ( long['support'] < long['resistance'] ) , long['Close'], np.nan )

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

# ========== query by activerecord =========
# orders = Orders.all 
# puts orders.first.buy_date
# puts orders.pluck(:buy_amount, :buy_date, :buy_price)
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