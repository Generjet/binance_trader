require "application_system_test_case"

class TradeSignalsTest < ApplicationSystemTestCase
  setup do
    @trade_signal = trade_signals(:one)
  end

  test "visiting the index" do
    visit trade_signals_url
    assert_selector "h1", text: "Trade signals"
  end

  test "should create trade signal" do
    visit trade_signals_url
    click_on "New trade signal"

    fill_in "Bot signal", with: @trade_signal.bot_signal
    fill_in "Buy zone", with: @trade_signal.buy_zone
    fill_in "Currency", with: @trade_signal.currency
    fill_in "D", with: @trade_signal.d
    fill_in "Date", with: @trade_signal.date
    fill_in "K", with: @trade_signal.k
    fill_in "Last close price", with: @trade_signal.last_close_price
    fill_in "Macd", with: @trade_signal.macd
    fill_in "Resistance", with: @trade_signal.resistance
    fill_in "Rsi", with: @trade_signal.rsi
    fill_in "Sell zone", with: @trade_signal.sell_zone
    fill_in "Support", with: @trade_signal.support
    click_on "Create Trade signal"

    assert_text "Trade signal was successfully created"
    click_on "Back"
  end

  test "should update Trade signal" do
    visit trade_signal_url(@trade_signal)
    click_on "Edit this trade signal", match: :first

    fill_in "Bot signal", with: @trade_signal.bot_signal
    fill_in "Buy zone", with: @trade_signal.buy_zone
    fill_in "Currency", with: @trade_signal.currency
    fill_in "D", with: @trade_signal.d
    fill_in "Date", with: @trade_signal.date
    fill_in "K", with: @trade_signal.k
    fill_in "Last close price", with: @trade_signal.last_close_price
    fill_in "Macd", with: @trade_signal.macd
    fill_in "Resistance", with: @trade_signal.resistance
    fill_in "Rsi", with: @trade_signal.rsi
    fill_in "Sell zone", with: @trade_signal.sell_zone
    fill_in "Support", with: @trade_signal.support
    click_on "Update Trade signal"

    assert_text "Trade signal was successfully updated"
    click_on "Back"
  end

  test "should destroy Trade signal" do
    visit trade_signal_url(@trade_signal)
    click_on "Destroy this trade signal", match: :first

    assert_text "Trade signal was successfully destroyed"
  end
end
