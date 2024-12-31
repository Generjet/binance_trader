#!/bin/bash

# Check for arguments
if [ -z "$2" ]; then
	cat << EOF >&2
Usage: binance-calc <coin-id> <target-price-usd>
EOF
exit 1
fi

# JSON Parser
# Credit: https://gist.github.com/cjus
function jsonval {
	    temp=`echo $json | sed 's/\\\\\//\//g' | sed 's/[{}]//g' | awk -v k="text" '{n=split($0,a,","); for (i=1; i<=n; i++) print a[i]}' | sed 's/\"\:\"/\|/g' | sed 's/[\,]/ /g' | sed 's/\"//g' | grep -w $prop`
	        echo ${temp##*|}
	}

	# Pretty colors
	RED='\033[1;31m'
	YELLOW='\033[1;33m'
	GREEN='\033[1;32m'
	WHITE='\033[0;37m'
	BOLD='\033[1;37m'

	# API Endpoint
	api='https://api.binance.com/api/v1/ticker/price?symbol='

	# JSON Property to extract
	prop='price'

	# Get input coin value in BTC
	json=`curl -s ${api}${1}BTC`
	coinval=`jsonval`

	# Get Bitcoin value in USD
	json=`curl -s ${api}BTCUSDT`
	btcval=`jsonval`

	# Calculate coin value in BTC
	coinval_usd=$(echo "$coinval * $btcval" | bc)

	# Calculate limit price in BTC
	limit_price_btc=$(printf %.8f $(echo "${2} / $btcval" | bc -l))

	# Calculate offset percent
	recovery_gain=$(printf %.2f $(echo "((${2}/$coinval_usd)*100)-100" | bc -l))

	echo -e "${BOLD}${1} Binance Calculations:"
	echo -e "${WHITE}Coin USD Value: ${YELLOW}\$${coinval_usd}"
	echo -e "${WHITE}Limit Price: ${RED}${limit_price_btc}"
	echo -e "${WHITE}Offset: ${GREEN}$recovery_gain%"
