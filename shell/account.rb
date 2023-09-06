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
client = Binance::Spot.new(key: ENV["API_KEY"], secret: ENV["API_SECRET"])
# Send a request to query BTCUSDT ticker
current_price = client.ticker_24hr(symbol: 'ETHUSDT')
lastPrice = current_price[:lastPrice].to_f
puts lastPrice
# Send a request to get account information
my_account = client.account

puts my_account
# ========== CRONJOB test ===========
File.open('account_binance.json',"a") { |f| f.write client.account }

abort "test end"
