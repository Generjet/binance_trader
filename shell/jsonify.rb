require 'json'

data_file = File.read('./account_binance.json')
first_hash = JSON.parse(data_file)
# first_hash['places_to_visit']['3'] = 'Madame Tussauds'

puts first_hash

# hash_data = { 
#     "name" => "Nikhil", 
#     "age" => 30, 
#     "city" => "Delhi" 
# }
# json_data = JSON.generate(hash_data)

# 2. ================== Read Signals ======================
# file = CSV.read("signals.csv")
# file = CSV.parse(File.read("orders.csv"), headers: true)
# CSV.foreach('signals.csv', :headers => true) do |row|
#     puts row['support']
#     puts row['time_period']
# end

# puts json_data