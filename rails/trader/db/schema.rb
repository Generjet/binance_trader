# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.0].define(version: 2023_08_04_101455) do
  create_table "orders", force: :cascade do |t|
    t.float "buy_amount"
    t.float "buy_price"
    t.datetime "buy_date"
    t.float "sell_amount"
    t.float "sell_price"
    t.datetime "sell_date"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "trade_signals", force: :cascade do |t|
    t.datetime "date"
    t.float "rsi"
    t.float "k"
    t.float "d"
    t.float "macd"
    t.float "support"
    t.float "resistance"
    t.float "buy_zone"
    t.float "sell_zone"
    t.string "currency"
    t.string "bot_signal"
    t.float "last_close_price"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

end
