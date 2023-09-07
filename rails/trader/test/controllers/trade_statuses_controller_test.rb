require "test_helper"

class TradeStatusesControllerTest < ActionDispatch::IntegrationTest
  setup do
    @trade_status = trade_statuses(:one)
  end

  test "should get index" do
    get trade_statuses_url
    assert_response :success
  end

  test "should get new" do
    get new_trade_status_url
    assert_response :success
  end

  test "should create trade_status" do
    assert_difference("TradeStatus.count") do
      post trade_statuses_url, params: { trade_status: { period: @trade_status.period, trade_status: @trade_status.trade_status } }
    end

    assert_redirected_to trade_status_url(TradeStatus.last)
  end

  test "should show trade_status" do
    get trade_status_url(@trade_status)
    assert_response :success
  end

  test "should get edit" do
    get edit_trade_status_url(@trade_status)
    assert_response :success
  end

  test "should update trade_status" do
    patch trade_status_url(@trade_status), params: { trade_status: { period: @trade_status.period, trade_status: @trade_status.trade_status } }
    assert_redirected_to trade_status_url(@trade_status)
  end

  test "should destroy trade_status" do
    assert_difference("TradeStatus.count", -1) do
      delete trade_status_url(@trade_status)
    end

    assert_redirected_to trade_statuses_url
  end
end
