require "application_system_test_case"

class OrdersTest < ApplicationSystemTestCase
  setup do
    @order = orders(:one)
  end

  test "visiting the index" do
    visit orders_url
    assert_selector "h1", text: "Orders"
  end

  test "should create order" do
    visit orders_url
    click_on "New order"

    fill_in "Buy amount", with: @order.buy_amount
    fill_in "Buy date", with: @order.buy_date
    fill_in "Buy price", with: @order.buy_price
    fill_in "Sell amount", with: @order.sell_amount
    fill_in "Sell date", with: @order.sell_date
    fill_in "Sell price", with: @order.sell_price
    click_on "Create Order"

    assert_text "Order was successfully created"
    click_on "Back"
  end

  test "should update Order" do
    visit order_url(@order)
    click_on "Edit this order", match: :first

    fill_in "Buy amount", with: @order.buy_amount
    fill_in "Buy date", with: @order.buy_date
    fill_in "Buy price", with: @order.buy_price
    fill_in "Sell amount", with: @order.sell_amount
    fill_in "Sell date", with: @order.sell_date
    fill_in "Sell price", with: @order.sell_price
    click_on "Update Order"

    assert_text "Order was successfully updated"
    click_on "Back"
  end

  test "should destroy Order" do
    visit order_url(@order)
    click_on "Destroy this order", match: :first

    assert_text "Order was successfully destroyed"
  end
end
