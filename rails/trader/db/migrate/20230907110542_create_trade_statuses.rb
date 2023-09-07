class CreateTradeStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :trade_statuses do |t|
      t.string :period
      t.string :trade_status

      t.timestamps
    end
  end
end
