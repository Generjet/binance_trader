require 'csv'
require 'binance'
# require 'mysql2'
require 'sqlite3'
require 'active_record'
require 'date'

# 1. ============= Create a new client instance. ==============
# ==== turshiltiih =====
# client = Binance::Spot.new(base_url: 'https://testnet.binance.vision')
# puts client.time
# ==== jinhene =======
client = Binance::Spot.new(key: ENV["bot_api_key"], secret: ENV["bot_api_secret"])
# Send a request to query BTCUSDT ticker
current_price = client.ticker_24hr(symbol: 'ETHUSDT')
# Send a request to get account information
my_account = client.account


# 2. ================== Read Signals ======================
# file = CSV.read("signals.csv")
# file = CSV.parse(File.read("orders.csv"), headers: true)
# puts file

# id,time_period,date,rsi,stoch,macd,support,resistance,buy_zone,sell_zone

CSV.foreach('signals.csv', :headers => true) do |row|
    puts row['support']
    puts row['time_period']
end

# 3. ================== Read Orders ================
# === GLOBAL variables ====
# date_time = DateTime.now
# curr_date_time = date_time.strftime "%d/%m/%Y  %H:%M:%S"
current_datetime = DateTime.now
puts current_datetime

# ===== establish connection ======
    ActiveRecord::Base.establish_connection( 
        :adapter => "sqlite3",
        :host => "localhost",
        :database => "../rails/trader/db/development.sqlite3"
       )
    # =====================
class Orders < ActiveRecord::Base
    self.table_name = 'orders'
        # has_many :table_relationship
end

# ========== query by activerecord =========

# # === insert ===
# order = Orders.new
# order.buy_signal = ARGV[0]
# order.buy_time = ARGV[1]
# order.buy_order = ARGV[2]
# order.buy_amount = ARGV[3]
# order.buy_price = ARGV[4]
# order.currency = ARGV[5]
# order.save

# === select ===
orders = Orders.all 
puts orders.first.buy_date
# puts orders.pluck(:buy_amount, :buy_date, :buy_price)

abort "DEBUG =====> DONE"


# 4. ============= Place an order ========================
# response = client.new_order(symbol: 'ETHUSDT', side: 'SELL', price: 1945, quantity: 0.0294, type: 'LIMIT', timeInForce: 'GTC')

# 5. ============== Update or Insert into Orders =========

