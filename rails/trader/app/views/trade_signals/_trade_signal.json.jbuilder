json.extract! trade_signal, :id, :date, :rsi, :k, :d, :macd, :support, :resistance, :buy_zone, :sell_zone, :currency, :bot_signal, :last_close_price, :created_at, :updated_at
json.url trade_signal_url(trade_signal, format: :json)
