class AddPeriodToTradeSignals < ActiveRecord::Migration[7.0]
  def change
    add_column :trade_signals, :period, :string
  end
end
