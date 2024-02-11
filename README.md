# SkyblockSniper

## Check out this bazaar flipping website, https://skyblock.bz

### Feel free to open up issue requests and I will try to assist you to the best of my ability.

## How to use:
[Here's a video some dude made that shows the process fairly well](https://youtu.be/ojzcvRCDqJ0)
[This is a video I made on installing a similar program but just replace the github url with this one.]((https://youtu.be/xPEZBK1SaUk))
### Step 1
Download Python 3.7.8. There's literally thousands of guides on how to do this so I'll assume you can figure it out yourself.

### Step 2
Either download this repository or just copy paste all the code from inside `SkyblockSniper.py` into a new file on your computer called `SkyblockSniper.py`, and all the text from `requirements.txt` into a new file on your computer called `requirements.txt`.

### Step 3
Run the command `pip install -r <path to requirements.txt>` in the command prompt (Window key + R, type cmd). For example, on my computer, the path to `requirements.txt` is `C:\Downloads\requirements.txt`, so I'd use `pip install -r C:\Downloads\requirements.txt`.

### Step 4
Run the file `SkyblockSniper.py` by going into command prompt and running the command `python <path to SkyblockSniper.py>`. For example, on my computer, the path to `SkyblockSniper.py` is `C:\Downloads\SkyblockSniper.py`, so I'd use `python C:\Downloads\SkyblockSniper.py`.

### Step 5
Now the script is running good and well. From here, you can just AFK on your island splitscreened watching Netflix or something. As soon as the script finds a good flip, you'll hear a low frequency beep for half a second, and the command to go to the auction is automatically put on your clipboard.

All you have to do is Ctrl+V every time you hear the beep, make sure it's not a scam (sometimes this happens with cosmetics or other market manipulation; can be prevented with NEU's average AH price thing), and then buy it.

## Basic Troubleshooting
> 'pip' is not recognized as an internal or external command, operable program or batch file.
>
Follow the first reply to [this stackoverflow post](https://stackoverflow.com/questions/23708898/), note that you'll have to open a new cmd window to apply the changes to PATH

> Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases
> 
Make sure Python's installation folder was added to your PATH variables properly, and follow the [other suggestions on this stackoverflow post](https://stackoverflow.com/questions/65348890/).

## How to know it works
### Change LOWEST_PRICE in SkyblockSniper.py line 27 to 5 and rerun the script
You should get a few results for (shittier) BIN flips. Change LOWEST_PRICE back to 999999 (or any price you want to be the lowest) once done.

### CMD should look something like this before any results:
![image](https://user-images.githubusercontent.com/61282104/132762683-76d65de2-48f1-4aea-b47e-51f9378d4bdf.png)

and like this after results:
![image](https://user-images.githubusercontent.com/61282104/132763043-07ba557b-25dd-43d5-af96-fee025ec1ad7.png)

#### Some statistics I noticed
Timing: For me it takes 8-10 seconds to refresh the AH, which happens every minute (that's an API-level limit).

Coins per hour: There were a few good snipes per hour (i.e. a baby yeti for 1.6 mil, reaper mask for 1 mil) but again, no clue where the 200 mil per hour numbers are coming from. My best guess is that they're saying that SOME hours they make 200 mil per hour, and as such that means it's technically correct

Here's approximately 7 hours worth of results (12am EST to 7am EST):
![image](https://user-images.githubusercontent.com/61282104/132677810-d349c84f-d704-40f9-88f5-56424c8bd788.png)

