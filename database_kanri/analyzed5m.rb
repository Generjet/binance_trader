

 # require 'mysql2'

 require 'sqlite3'
 require 'active_record'
 require 'date'
 
 # === GLOBAL variables ====
 # date_time = DateTime.now
 # curr_date_time = date_time.strftime "%d/%m/%Y  %H:%M:%S"
 current_datetime = DateTime.now
 puts current_datetime
 
 # ===== establish connection ======
     ActiveRecord::Base.establish_connection( 
         :adapter => "sqlite3",
         :host => "localhost",
         :database => "../db/development.sqlite3"
        )
     # =====================
 class Orders < ActiveRecord::Base
     self.table_name = 'orders'
         # has_many :table_relationship
 end
 
 # ========== query by activerecord =========
 
 # === insert ===
 order = Orders.new
 order.buy_signal = ARGV[0]
 order.buy_time = ARGV[1]
 order.buy_order = ARGV[2]
 order.buy_amount = ARGV[3]
 order.buy_price = ARGV[4]
 order.currency = ARGV[5]
 order.save
 
 # === select ===
 orders = Orders.all 
 puts orders.pluck(:currency, :buy_price)
 
 abort "DEBUG =====> DONE"
 
    # === update ===
    # order = Orders.find(1)
    # order.buy_signal = "SELL"
    # order.save

    # === delete ===
    # order = Orders.find(1)
    # order.destroy 
    # ========================================  end of file  ========================================