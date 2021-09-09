import asyncio
import re
import threading
import winsound
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

import pandas as pd
import requests

frequency = 500
duration = 500

c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0")
resp = c.json()
now = resp['lastUpdated']
toppage = resp['totalPages']

results = []
prices = {}

REFORGES = [" ✦", "⚚ ", " ✪", "✪", "Stiff ", "Lucky ", "Jerry's ", "Dirty ", "Fabled ", "Suspicious ", "Gilded ", "Warped ", "Withered ", "Bulky ", "Stellar ", "Heated ", "Ambered ", "Fruitful ", "Magnetic ", "Fleet ", "Mithraic ", "Auspicious ", "Refined ", "Headstrong ", "Precise ", "Spiritual ", "Moil ", "Blessed ", "Toil ", "Bountiful ", "Candied ", "Submerged ", "Reinforced ", "Cubic ", "Warped ", "Undead ", "Ridiculous ", "Necrotic ", "Spiked ", "Jaded ", "Loving ", "Perfect ", "Renowned ", "Giant ", "Empowered ", "Ancient ", "Sweet ", "Silky ", "Bloody ", "Shaded ", "Gentle ", "Odd ", "Fast ", "Fair ", "Epic ", "Sharp ", "Heroic ", "Spicy ", "Legendary ", "Deadly ", "Fine ", "Grand ", "Hasty ", "Neat ", "Rapid ", "Unreal ", "Awkward ", "Rich ", "Clean ", "Fierce ", "Heavy ", "Light ", "Mythic ", "Pure ", "Smart ", "Titanic ", "Wise ", "Bizarre ", "Itchy ", "Ominous ", "Pleasant ", "Pretty ", "Shiny ", "Simple ", "Strange ", "Vivid ", "Godly ", "Demonic ", "Forceful ", "Hurtful ", "Keen ", "Strong ", "Superior ", "Unpleasant ", "Zealous "]

START_TIME = default_timer()

def fetch(session, page):
    global toppage
    base_url = "https://api.hypixel.net/skyblock/auctions?page="
    with session.get(base_url + page) as response:
        data = response.json()
        toppage = data['totalPages']
        if data['success']:
            toppage = data['totalPages']
            for auction in data['auctions']:
                if not auction['claimed'] and 'bin' in auction:
                    index = re.sub("\[[^\]]*\]", "", auction['item_name']) + auction['tier']
                    for reforge in REFORGES: index = index.replace(reforge, "")
                    if index in prices:
                        if prices[index][0] > auction['starting_bid']:
                            prices[index][1] = prices[index][0]
                            prices[index][0] = auction['starting_bid']
                        elif prices[index][1] > auction['starting_bid']:
                            prices[index][1] = auction['starting_bid']
                    else:
                        prices[index] = [float("inf"), float("inf")]

                    if prices[index][1] > 1000000 and prices[index][0] < prices[index][1]/2 and auction['start']+60000 > now:
                        results.append([auction['uuid'], auction['item_name'], auction['starting_bid'], index])
        return data

async def get_data_asynchronous():
    pages = [str(x) for x in range(toppage)]
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, page) # Allows us to pass in multiple arguments to `fetch`
                )
                for page in pages if int(page) < toppage
            ]
            for response in await asyncio.gather(*tasks):
                pass

def main():
    global results, prices, START_TIME
    START_TIME = default_timer()
    results = []
    prices = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)
    done = default_timer() - START_TIME
    results = [[entry, prices[entry[3]][1]] for entry in results if (entry[2] > 1000000 and prices[entry[3]][1] != float('inf') and prices[entry[3]][0] == entry[2] and prices[entry[3]][0] < prices[entry[3]][1]/2)]
    if len(results):
        df=pd.DataFrame(['/viewauction ' + str(max(results, key=lambda entry:entry[0][2])[0][0])])
        df.to_clipboard(index=False,header=False)
        winsound.Beep(frequency, duration)
        print(results, done, len(results))

main()

def test():
    global now, toppage
    threading.Timer(1, test).start()
    c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0")
    resp = c.json()
    tempnow = resp['lastUpdated']
    if tempnow > now:
        now = tempnow
        toppage = resp['totalPages']
        main()

test()
