import asyncio

from binance import AsyncClient


async def main():

    client = await AsyncClient.create()
    exchange_info = await client.get_exchange_info()
    tickers = await client.get_all_tickers()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())