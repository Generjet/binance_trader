class CreateTradeSignals < ActiveRecord::Migration[7.0]
  def change
    create_table :trade_signals do |t|
      t.datetime :date
      t.float :rsi
      t.float :k
      t.float :d
      t.float :macd
      t.float :support
      t.float :resistance
      t.float :buy_zone
      t.float :sell_zone
      t.string :currency
      t.string :bot_signal
      t.float :last_close_price

      t.timestamps
    end
  end
end
