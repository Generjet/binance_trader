class CreateOrders < ActiveRecord::Migration[7.0]
  def change
    create_table :orders do |t|
      t.float :buy_amount
      t.float :buy_price
      t.datetime :buy_date
      t.float :sell_amount
      t.float :sell_price
      t.datetime :sell_date

      t.timestamps
    end
  end
end
