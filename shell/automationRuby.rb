puts "Automation done by Ruby language"

# /home/minimachine/binance_trader/shell
File.open('/home/minimachine/binance_trader/shell/rubyAutomationResult.txt',"a") { |f| f.write "Ruby Automation is done at #{Time.now} successfully \n" }
# File.open('rubyAutomationResult.txt',"a") { |f| f.write "Ruby Automation is done at #{Time.now} successfully \n" }