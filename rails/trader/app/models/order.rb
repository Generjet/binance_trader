class Order < ApplicationRecord
    before_create :set_trade_type
    # after update calculate profit
    after_save :calculate_profit

    private
    def calculate_profit
        self.profit  = self.sell_price - self.buy_price
        self.save
    end

    def set_trade_type
        self.trade_type ||= 'channel' # 1. stop_loss 2. no_resistance 3. channel (default)
        self.period ||= '5min' # 5min,15min,30min,1h,4h,1d,1M
    end
end
