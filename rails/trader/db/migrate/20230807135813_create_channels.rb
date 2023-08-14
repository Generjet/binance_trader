class CreateChannels < ActiveRecord::Migration[7.0]
  def change
    create_table :channels do |t|
      t.float :support
      t.float :resistance
      t.string :channel_status

      t.timestamps
    end
  end
end
