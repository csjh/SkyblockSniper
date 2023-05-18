import asyncio
import re
import os
import json
import aiohttp as aiohttp
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import time
import pandas as pd
import requests
from plyer import notification

op = os.name == 'nt'
if op:
    import winsound

c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0")
resp = c.json()
now = resp['lastUpdated']
toppage = resp['totalPages']

results = []
prices = {}

# stuff to remove
with open("reforges.json", "r") as file:
    REFORGES = json.load(file)['reforges']

# Constant for the lowest priced item you want to be shown to you; feel free to change this
LOWEST_PRICE = 5

# Constant to turn on/off desktop notifications
NOTIFY = False

# Constant for the lowest percent difference you want to be shown to you; feel free to change this
LOWEST_PERCENT_MARGIN = 1 / 2

START_TIME = default_timer()


async def fetch(session, page):
    global toppage
    base_url = "https://api.hypixel.net/skyblock/auctions?page="

    async with session.get(base_url + page) as response:
        data = await response.json()

    if not data['success']:
        return None

    toppage = data['totalPages']

    for auction in data['auctions']:
        if auction['claimed'] or not auction['bin'] or "Furniture" in auction["item_lore"]:
            continue

        index = re.sub(r"\[[^\]]*\]", "", auction['item_name']) + auction['tier']

        for reforge in REFORGES:
            index = index.replace(reforge[0], "").strip()

        if index in prices:
            if prices[index][0] > auction['starting_bid']:
                prices[index][1] = prices[index][0]
                prices[index][0] = auction['starting_bid']
            elif prices[index][1] > auction['starting_bid']:
                prices[index][1] = auction['starting_bid']
        else:
            prices[index] = [auction['starting_bid'], float("inf")]

        if (
                prices[index][1] > LOWEST_PRICE
                and prices[index][0] / prices[index][1] < LOWEST_PERCENT_MARGIN
                and auction['start'] + 60000 > now
        ):
            results.append([auction['uuid'], auction['item_name'], auction['starting_bid'], index])

    return data


async def get_data_asynchronous():
    # puts all the page strings
    pages = [str(x) for x in range(toppage)]
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, page)  # Allows us to pass in multiple arguments to `fetch`
                )
                # runs for every page
                for page in pages if int(page) < toppage
            ]
            for response in await asyncio.gather(*tasks):
                pass


async def main():
    global results, prices, START_TIME
    START_TIME = default_timer()
    results = []
    prices = {}

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.ensure_future(fetch(session, str(page)))
            for page in range(toppage)
        ]
        await asyncio.gather(*tasks)

    if len(results):
        results = [
            [entry, prices[entry[3]][1]]
            for entry in results
            if LOWEST_PRICE < entry[2] == prices[entry[3]][0]
               and prices[entry[3]][1] != float('inf')
               and prices[entry[3]][0] / prices[entry[3]][1] < LOWEST_PERCENT_MARGIN
        ]

    if len(results):
        if NOTIFY:
            notification.notify(
                title=max(results, key=lambda entry: entry[1])[0][1],
                message="Lowest BIN: " + f'{max(results, key=lambda entry: entry[1])[0][2]:,}' + "\nSecond Lowest: " +
                        f'{max(results, key=lambda entry: entry[1])[1]:,}',
                app_icon=None,
                timeout=4,
            )

        df = pd.DataFrame(['/viewauction ' + str(max(results, key=lambda entry: entry[1])[0][0])])
        df.to_clipboard(index=False, header=False)

        done = default_timer() - START_TIME
        if op:
            winsound.Beep(500, 500)  # emits a frequency 500hz, for 500ms
        for result in results:
            print("Auction UUID: " + str(result[0][0]) + " | Item Name: " + str(result[0][1]) +
                  " | Item price: {:,}".format(result[0][2]), " | Second lowest BIN: {:,}".format(result[1]) +
                  " | Time to refresh AH: " + str(round(done, 2)))
        print("\nLooking for auctions...")


print("Looking for auctions...")


async def run_program():
    await main()


async def dostuff():
    global now, toppage

    while True:
        if time.time() * 1000 > now + 1000:
            prevnow = now
            now = float('inf')
            c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0").json()
            if c['lastUpdated'] != prevnow:
                now = c['lastUpdated']
                toppage = c['totalPages']
                await main()
            else:
                now = prevnow
        await asyncio.sleep(0.25)


async def main_loop():
    task1 = asyncio.create_task(run_program())
    task2 = asyncio.create_task(dostuff())
    await asyncio.gather(task1, task2)


if __name__ == '__main__':
    asyncio.run(main_loop())
