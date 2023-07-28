#/bin/bash

echo "Bot started to act"

# 1. call python script for buy/sell signal
python analyze.py

sleep 1
# result=`python analyze.py "4h"`
result=`python analyze.py`
if [ "$result" == "Buy" ]; then
    echo "We need to Buy crypto, hurry up!"
elif [ "$result" == "Sell" ]; then
    echo "We need to Sell crypto, now!"
else 
    echo "Wait, wait, wait!"
fi