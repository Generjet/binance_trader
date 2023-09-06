import datetime

file = open(r'C:\Users\Goodluck\Documents\signals.txt','a')
file.write(f'{datetime.datetime.now()} - /home/robin/miniconda3/python CRONJOB ****** - ****** ARDUINO DATA LOGGER TEST -> The script ran\n')
print("signals.txt TEST")