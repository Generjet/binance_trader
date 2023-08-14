class AddPeriodToOrders < ActiveRecord::Migration[7.0]
  def change
    add_column :orders, :period, :string
    add_column :orders, :buy_signal_id, :integer
    add_column :orders, :sell_signal_id, :integer
  end
end
