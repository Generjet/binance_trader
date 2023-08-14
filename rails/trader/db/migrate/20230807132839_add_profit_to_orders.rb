class AddProfitToOrders < ActiveRecord::Migration[7.0]
  def change
    add_column :orders, :profit, :float
    add_column :orders, :channel_id, :integer
    add_column :orders, :trade_type, :string
  end
end
