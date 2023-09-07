require "application_system_test_case"

class TradeStatusesTest < ApplicationSystemTestCase
  setup do
    @trade_status = trade_statuses(:one)
  end

  test "visiting the index" do
    visit trade_statuses_url
    assert_selector "h1", text: "Trade statuses"
  end

  test "should create trade status" do
    visit trade_statuses_url
    click_on "New trade status"

    fill_in "Period", with: @trade_status.period
    fill_in "Trade status", with: @trade_status.trade_status
    click_on "Create Trade status"

    assert_text "Trade status was successfully created"
    click_on "Back"
  end

  test "should update Trade status" do
    visit trade_status_url(@trade_status)
    click_on "Edit this trade status", match: :first

    fill_in "Period", with: @trade_status.period
    fill_in "Trade status", with: @trade_status.trade_status
    click_on "Update Trade status"

    assert_text "Trade status was successfully updated"
    click_on "Back"
  end

  test "should destroy Trade status" do
    visit trade_status_url(@trade_status)
    click_on "Destroy this trade status", match: :first

    assert_text "Trade status was successfully destroyed"
  end
end
