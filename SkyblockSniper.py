import asyncio
import re
import os
op = os.name == 'nt'
if op: import winsound
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import time

import pandas as pd
import requests

from plyer import notification

c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0")
resp = c.json()
now = resp['lastUpdated']
toppage = resp['totalPages']

results = []
prices = {}

# stuff to remove
REFORGES = [" ✦", "⚚ ", "◆ "," ✪", "✪","➋", "➌","➎", "Extremely ","Zooming ", "Salty ","Fortunate ", "➊","Menacing ","Very ","Festive ","Astute ","Blended ","Thicc ", "Sturdy ", "Glistening ", "Honored ","Rugged ","Sharp ","Excellent ","Honored ","Rugged ", "Strengthened ","Stiff ", "Robust ", "Lush ","Waxed ","Bustling ","Lucky ", "Jerry's ", "Dirty ", "Fabled ", "Suspicious ", "Gilded ", "Warped ", "Withered ", "Bulky ", "Stellar ", "Heated ", "Ambered ", "Fruitful ", "Magnetic ", "Fleet ", "Mithraic ", "Auspicious ", "Refined ", "Headstrong ", "Precise ", "Spiritual ", "Moil ", "Blessed ", "Toil ", "Bountiful ", "Candied ", "Submerged ", "Reinforced ", "Cubic ", "Warped ", "Undead ", "Ridiculous ", "Necrotic ", "Spiked ", "Jaded ", "Loving ", "Perfect ", "Renowned ", "Giant ", "Empowered ", "Ancient ", "Sweet ", "Silky ", "Bloody ", "Shaded ", "Gentle ", "Odd ", "Fast ", "Fair ", "Epic ", "Sharp ", "Heroic ", "Spicy ", "Legendary ", "Deadly ", "Fine ", "Grand ", "Hasty ", "Neat ", "Rapid ", "Unreal ", "Awkward ", "Rich ", "Clean ", "Fierce ", "Heavy ", "Light ", "Mythic ", "Pure ", "Smart ", "Titanic ", "Wise ", "Bizarre ", "Itchy ", "Ominous ", "Pleasant ", "Pretty ", "Shiny ", "Simple ", "Strange ", "Vivid ", "Godly ", "Demonic ","Brilliant ", "Forceful ", "Hurtful ", "Keen ", "Strong ", "Superior ", "Unpleasant ", "Zealous "]

# Constant for the lowest priced item you want to be shown to you; feel free to change this
LOWEST_PRICE = 250000

# Constant to turn on/off desktop notifications
NOTIFY = False

# Constant for the lowest median you want to be shown to you; feel free to change this
Minimum_Median_Margin = 1.2

# Constant for the lowest percent difference you want to be shown to you; feel free to change this
LOWEST_PERCENT_MARGIN = 0.5

START_TIME = default_timer()

def fetch(session, page):
    global toppage
    base_url = "https://api.hypixel.net/skyblock/auctions?page="
    with session.get(base_url + page) as response:
        # puts response in a dict
        data = response.json()
        toppage = data['totalPages']
        if data['success']:
            toppage = data['totalPages']
            for auction in data['auctions']:
                if not auction['claimed'] and auction['bin'] == True and not "Furniture" in auction["item_lore"]: # if the auction isn't a) claimed and is b) BIN
                    # removes level if it's a pet, also 
                    index = re.sub("\[[^\]]*\]", "", auction['item_name']) + auction['tier']
                    # removes reforges and other yucky characters
                    for reforge in REFORGES: index = index.replace(reforge, "")
                    # if the current item already has a price in the prices map, the price is updated
                    if index in prices:
                        if prices[index][0] > auction['starting_bid']:
                            prices[index][1] = prices[index][0]
                            prices[index][0] = auction['starting_bid']
                        elif prices[index][1] > auction['starting_bid']:
                            prices[index][1] = auction['starting_bid']
                    # otherwise, it's added to the prices map
                    else:
                        prices[index] = [auction['starting_bid'], float("inf")]
                    # Compare median with the item price
                    if  prices[index][1] > LOWEST_PRICE and prices[index][0]/prices[index][1] < LOWEST_PERCENT_MARGIN and auction['start']+60000 > now:
                        cofl_data = fetch_cofl(auction['item_name'])
                        #remove if name contains "New Year Cake" or any unwanted flips

                        # if "New Year" not in auction['item_name'] and "Talbot" not in auction['item_name'] and "Rune" not in auction['item_name'] and "Restoration" not in auction['item_name']:
                        #         cofl_data = fetch_cofl(auction['item_name'])
                        # else:
                        #     cofl_data = None
                        if cofl_data is not None:
                            median_price = cofl_data['median']
                        else:
                            print("Failed to fetch COFL data for", auction['item_name'])
                            median_price = None
                        if median_price is not None and median_price / (auction['starting_bid']) > Minimum_Median_Margin:
                            min_price = cofl_data['min']
                            if auction['starting_bid'] > min_price:
                                results.append([auction['uuid'], auction['item_name'], auction['starting_bid'], index])
        return data

# Function to extract the median price from the auction data
def fetch_cofl(item_name):
    #remove all reforge tags
    item_name = re.sub("\[[^\]]*\]", "", item_name)
    for reforge in REFORGES: item_name = item_name.replace(reforge, "") 
    median_url = f"https://sky.coflnet.com/api/item/price/{item_name.replace(' ', '_')}"
    median_response = requests.get(median_url)
    
    if median_response.status_code == 200:
        
        median_data = median_response.json()
        return median_data
    else:
        print(f"Error fetching median price for {item_name}")
        return None

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
                    *(session, page) # Allows us to pass in multiple arguments to `fetch`
                )
                # runs for every page
                for page in pages if int(page) < toppage
            ]
            for response in await asyncio.gather(*tasks):
                pass



def main():
    # Resets variables
    global results, prices, START_TIME
    START_TIME = default_timer()
    results = []
    prices = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)
    
    # Makes sure all the results are still up to date
    if len(results): 
        results = [[entry, prices[entry[3]][1]] for entry in results if (entry[2] > LOWEST_PRICE and prices[entry[3]][1] != float('inf') and prices[entry[3]][0] == entry[2] and prices[entry[3]][0]/prices[entry[3]][1] < LOWEST_PERCENT_MARGIN)]
    
    if len(results): # if there's results to print

        if NOTIFY: 
            notification.notify(
                title = max(results, key=lambda entry:entry[1])[0][1],
                message = "Lowest BIN: " + f'{max(results, key=lambda entry:entry[1])[0][2]:,}' + "\nSecond Lowest: " + f'{max(results, key=lambda entry:entry[1])[1]:,}',
                app_icon = None,
                timeout = 4,
            )
        df=pd.DataFrame(['/viewauction ' + str(max(results, key=lambda entry:entry[1])[0][0])])
        df.to_clipboard(index=False,header=False) # copies most valuable auction to clipboard (usually just the only auction cuz very uncommon for there to be multiple
        done = default_timer() - START_TIME
        if op: winsound.Beep(500, 500) # emits a frequency 500hz, for 500ms
        for result in results:
            median_price = (fetch_cofl(result[0][1])['median'])
            print("Auction UUID: " + str(result[0][0]) + " | Item Name: " + str(result[0][1]) + " | Item price: {:,}".format(result[0][2]) + " | Median Item Price: {:,.2f}".format(median_price) + " | Second lowest BIN: {:,}".format(result[1]) + " | Time to refresh AH: " + str(round(done, 2)))
        print("\nLooking for auctions...")

print("Looking for auctions...")
main()

def dostuff():
    global now, toppage

    # if 60 seconds have passed since the last update
    if time.time()*1000 > now + 60000:
        prevnow = now
        now = float('inf')
        c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0").json()
        if c['lastUpdated'] != prevnow:
            now = c['lastUpdated']
            toppage = c['totalPages']
            main()
        else:
            now = prevnow
    time.sleep(0.05)

while True:
    dostuff()
