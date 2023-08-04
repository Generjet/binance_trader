json.extract! order, :id, :buy_amount, :buy_price, :buy_date, :sell_amount, :sell_price, :sell_date, :created_at, :updated_at
json.url order_url(order, format: :json)
