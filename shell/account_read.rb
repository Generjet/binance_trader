require 'json'

data_file = File.read('./account_binance')
result_new = eval(data_file)
# puts result_new.instance_of? String
# puts result_new.instance_of? Hash

puts result_new.keys
puts "======== BALANCES ======="
puts result_new[:balances]
puts "======= USDT ========"

usdt = Hash.new
result_new[:balances].each do |coin|
    if coin[:asset] == 'USDT'
        usdt = coin
        # puts usdt[:free]
    end
end

puts "==== FREE USDT ===="
puts usdt[:free]
puts usdt[:locked]