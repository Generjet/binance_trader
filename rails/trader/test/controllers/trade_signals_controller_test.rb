require "test_helper"

class TradeSignalsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @trade_signal = trade_signals(:one)
  end

  test "should get index" do
    get trade_signals_url
    assert_response :success
  end

  test "should get new" do
    get new_trade_signal_url
    assert_response :success
  end

  test "should create trade_signal" do
    assert_difference("TradeSignal.count") do
      post trade_signals_url, params: { trade_signal: { bot_signal: @trade_signal.bot_signal, buy_zone: @trade_signal.buy_zone, currency: @trade_signal.currency, d: @trade_signal.d, date: @trade_signal.date, k: @trade_signal.k, last_close_price: @trade_signal.last_close_price, macd: @trade_signal.macd, resistance: @trade_signal.resistance, rsi: @trade_signal.rsi, sell_zone: @trade_signal.sell_zone, support: @trade_signal.support } }
    end

    assert_redirected_to trade_signal_url(TradeSignal.last)
  end

  test "should show trade_signal" do
    get trade_signal_url(@trade_signal)
    assert_response :success
  end

  test "should get edit" do
    get edit_trade_signal_url(@trade_signal)
    assert_response :success
  end

  test "should update trade_signal" do
    patch trade_signal_url(@trade_signal), params: { trade_signal: { bot_signal: @trade_signal.bot_signal, buy_zone: @trade_signal.buy_zone, currency: @trade_signal.currency, d: @trade_signal.d, date: @trade_signal.date, k: @trade_signal.k, last_close_price: @trade_signal.last_close_price, macd: @trade_signal.macd, resistance: @trade_signal.resistance, rsi: @trade_signal.rsi, sell_zone: @trade_signal.sell_zone, support: @trade_signal.support } }
    assert_redirected_to trade_signal_url(@trade_signal)
  end

  test "should destroy trade_signal" do
    assert_difference("TradeSignal.count", -1) do
      delete trade_signal_url(@trade_signal)
    end

    assert_redirected_to trade_signals_url
  end
end
