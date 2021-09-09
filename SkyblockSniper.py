import asyncio
import re
import threading
import winsound
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

import pandas as pd
import requests

c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0")
resp = c.json()
now = resp['lastUpdated']
toppage = resp['totalPages']

results = []
prices = {}

# stuff to remove
REFORGES = [" ✦", "⚚ ", " ✪", "✪", "Stiff ", "Lucky ", "Jerry's ", "Dirty ", "Fabled ", "Suspicious ", "Gilded ", "Warped ", "Withered ", "Bulky ", "Stellar ", "Heated ", "Ambered ", "Fruitful ", "Magnetic ", "Fleet ", "Mithraic ", "Auspicious ", "Refined ", "Headstrong ", "Precise ", "Spiritual ", "Moil ", "Blessed ", "Toil ", "Bountiful ", "Candied ", "Submerged ", "Reinforced ", "Cubic ", "Warped ", "Undead ", "Ridiculous ", "Necrotic ", "Spiked ", "Jaded ", "Loving ", "Perfect ", "Renowned ", "Giant ", "Empowered ", "Ancient ", "Sweet ", "Silky ", "Bloody ", "Shaded ", "Gentle ", "Odd ", "Fast ", "Fair ", "Epic ", "Sharp ", "Heroic ", "Spicy ", "Legendary ", "Deadly ", "Fine ", "Grand ", "Hasty ", "Neat ", "Rapid ", "Unreal ", "Awkward ", "Rich ", "Clean ", "Fierce ", "Heavy ", "Light ", "Mythic ", "Pure ", "Smart ", "Titanic ", "Wise ", "Bizarre ", "Itchy ", "Ominous ", "Pleasant ", "Pretty ", "Shiny ", "Simple ", "Strange ", "Vivid ", "Godly ", "Demonic ", "Forceful ", "Hurtful ", "Keen ", "Strong ", "Superior ", "Unpleasant ", "Zealous "]
FURNITURE = set(["Carpentry Table", "Stool", "Coffee Table", "Dining Chair", "Dining Table", "Minion Chair", "Dark Oak Chair", "Flower Pot", "Dark Oak Bench", "Dark Oak Table", "Armor Stand", "Scarecrow", "Desk", "Bookcase", "Small Shelves", "Weapon Rack", "Fire Pit", "Tiki Torch", "Fireplace", "Furnace+", "Chest Storage", "Weapon Rack+", "Hay Bed", "Large Bed", "Water Trough", "Food Trough", "Medium Shelves", "Crafting Table+", "Wood Chest+", "Diamond Chest+", "Emerald Chest+", "Iron Chest+", "Gold Chest+", "Lapis Chest+", "Redstone Chest+", "Ender Chest+", "Endstone Chest+", "Brewing+", "Enchanting Table+", "Blacksmith+", "Skull Chest++", "Grandfather Clock", "Personal Harp", "Hologram", "Hypixel Sandcastle", "Beach Chair", "Beach Ball", "Picnic Set", "Beach Chair+", "Red Tent", "Cola Cooler", "Illusion Glass", "Flying Bats", "Halloween Candles", "Candy Bowl", "Stacked Pumpkins", "Ghost Book", "X PEDESTAL", "Zombie Grave", "Cauldron", "Present Stack", "Stocking", "Nutcracker", "Small Holiday Tree", "Garland", "Tall Holiday Tree", "Candle Arch", "Derpy Snowman", "Egg Pile", "Easter Basket", "Bunny", "Chick Nest", "Bunny Jerry", "Life Preserver", "BBQ Grill", "Dingy", "Coffin", "Mummy Candle", "Crystal Ball", "Star Decorations", "Reindeer Plush", "Sled", "Wreath", "Gingerbread House", "Egg Stack", "Flower Bed", "Carrot Patch", "Hay Bale", "Rabbit Hutch", "Chicken Coop", "Deck Chair", "Beach Umbrella", "Surfboard", "Mini Sandcastle"])

# Constant for the lowest priced item you want to be shown to you; feel free to change this
LOWEST_PRICE = 1000000

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
                if not auction['claimed'] and 'bin' in auction and auction['item_name'] not in FURNITURE: # if the auction isn't a) claimed and is b) BIN
                    # removes level if it's a pet
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
                        
                    # if the auction fits in some parameters
                    if prices[index][1] > LOWEST_PRICE and prices[index][0] < prices[index][1]/2 and auction['start']+60000 > now:
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
    results = [[entry, prices[entry[3]][1]] for entry in results if (entry[2] > LOWEST_PRICE and prices[entry[3]][1] != float('inf') and prices[entry[3]][0] == entry[2] and prices[entry[3]][0] < prices[entry[3]][1]/2)]
    
    if len(results): # if there's results to print
        df=pd.DataFrame(['/viewauction ' + str(max(results, key=lambda entry:entry[0][2])[0][0])])
        df.to_clipboard(index=False,header=False) # copies most valuable auction to clipboard (usually just the only auction cuz very uncommon for there to be multiple
        
        winsound.Beep(500, 500) # emits a frequency 500hz, for 500ms
        
        done = default_timer() - START_TIME
        for result in results:
            print("Auction UUID: " + str(result[0][0]) + " | Item Name: " + str(result[0][1]) + " | Item price: {:,}".format(result[0][2]), " | Second lowest BIN: {:,}".format(result[1]) + " | Time to refresh AH: " + str(done))
        print()

main()

def dostuff():
    global now, toppage
    threading.Timer(1, dostuff).start()
    
    # gets first page to initialize some variables
    c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0")
    resp = c.json()
    tempnow = resp['lastUpdated']
    
    # if the new time is larger than the old time, main is executed
    if tempnow > now:
        now = tempnow
        toppage = resp['totalPages']
        main()

dostuff()
