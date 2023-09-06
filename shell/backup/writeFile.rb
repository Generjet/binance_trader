# file = File.open('ruby_log.txt')

File.open('ruby_schedule_log.txt',"a") { |f| f.write "The row #{Time.now} test done \n"}