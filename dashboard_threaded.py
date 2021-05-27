import requests_html
from bs4 import BeautifulSoup
import re
import time
import os
import numpy as np
from termcolor import colored
import textwrap as tw
from tabulate import tabulate
import curses
import threading
from pynput.keyboard import Key, Listener
import keyboard

# initialize links to scrape
URLs_crypto = []
URLs_crypto.append('https://coinmarketcap.com/currencies/monero/')
URLs_crypto.append('https://coinmarketcap.com/currencies/basic-attention-token/')
URLs_crypto.append('https://coinmarketcap.com/currencies/bitcoin/')
URLs_crypto.append('https://coinmarketcap.com/currencies/ethereum/')
URLs_crypto.append('https://coinmarketcap.com/currencies/presearch/')
URLs_crypto.append('https://coinmarketcap.com/currencies/numeraire/')
URLs_crypto.append('https://coinmarketcap.com/currencies/the-graph/')
URLs_crypto.append('https://coinmarketcap.com/currencies/nucypher/')
URLs_crypto.append('https://coinmarketcap.com/currencies/stellar/')
URLs_crypto.append('https://coinmarketcap.com/currencies/compound/')
URLs_crypto.append('https://coinmarketcap.com/currencies/skale-network/')
URLs_crypto.append('https://coinmarketcap.com/currencies/celo/')
URLs_crypto.append('https://coinmarketcap.com/currencies/uma/')
URLs_crypto.append('https://coinmarketcap.com/currencies/ampleforth/')
URLs_crypto.append('https://coinmarketcap.com/currencies/dogecoin/')
URLs_crypto.append('https://coinmarketcap.com/currencies/grin/')
URLs_crypto.append('https://coinmarketcap.com/currencies/polygon/')
URLs_crypto.append('https://coinmarketcap.com/currencies/picoin/')
num_crypto_URLs=len(URLs_crypto)
URLs_stocks = []
URLs_stocks.append('https://www.marketwatch.com/investing/stock/gme')
URLs_stocks.append('https://www.marketwatch.com/investing/stock/amc')
URLs_stocks.append('https://www.marketwatch.com/investing/stock/bb')
URLs_stocks.append('https://www.marketwatch.com/investing/stock/xmrusd')
num_stocks_URLs=len(URLs_stocks)

# initialize terminal and header sizes
size = os.get_terminal_size()
width = size[0]
height = size[1]
header_height = 2
table_header_height = 2

# initialize ncurses screen and windows for the header and tables
screen = curses.initscr()
# prevent getkey() from refreshing automatically
screen.refresh()
# uncomment for non-blocking getkey()
screen.nodelay(True) 
curses.curs_set(0) # make cursor invisible
curses.noecho()
screen.keypad(True)
title_window = curses.newwin(header_height,width,0,0)
table_height = 2+num_crypto_URLs+num_stocks_URLs
table_pad = curses.newpad(table_height,width)
title_window.addstr("The Almighty Dashboard \n")
title_window.refresh()

# initialize storage for data
names_crypto = ["unloaded"]*num_crypto_URLs
prices_crypto = [0.0]*num_crypto_URLs
elapsed_crypto = [0.0]*num_crypto_URLs
start_crypto = [time.time()]*num_crypto_URLs
names_stocks = ["unloaded"]*num_stocks_URLs
prices_stocks = [0.0]*num_stocks_URLs
elapsed_stocks = [0.0]*num_stocks_URLs
start_stocks = [time.time()]*num_stocks_URLs

# initialize flag for orderly stopping of all threads
stop_all=False
# initialize table position for scrolling with arrow keys
table_pos=0
resize_lock = threading.Lock()
# define clear function to clear terminal before exiting
clear = lambda: os.system('clear')

# define functions for scraping links
def getPrice_crypto(URL,i,s):
    while (not stop_all):
        start = time.time()

        try:
            session = requests_html.HTMLSession()
            page = session.get(URL)
            soup = BeautifulSoup(page.content, 'html.parser')
            price = soup.find(class_=re.compile("^priceValue")).get_text()
            name = soup.find(class_=re.compile("^nameSymbol")).get_text()
            prices_crypto[i] = price
            names_crypto[i] = name
            start_crypto[i] = start
        except:
            prices_crypto[i] = "FAILED"

        end = time.time()
        elapsed = (end-start)
        if (elapsed<s):
            time.sleep(s-elapsed)

def getPrice_stocks(URL,i,s):
    while (not stop_all):
        start = time.time()

        try:
            session = requests_html.HTMLSession()
            page = session.get(URL)
            soup = BeautifulSoup(page.content, 'html.parser')
            price = soup.find_all(class_=re.compile("^value$"), field="Last")[0].get_text()
            name = soup.find(class_="company__ticker").get_text()
            prices_stocks[i] = "$" + str(price)
            names_stocks[i] = name
            start_stocks[i] = start
        except:
            prices_stocks[i] = "FAILED"

        end = time.time()
        elapsed = (end-start)
        if (elapsed<s):
            time.sleep(s-elapsed)

# define function for drawing screen
def draw(s):
    while (not stop_all):
        start = time.time()
        global size, width, height
        size = os.get_terminal_size()
        width = size[0]
        height = size[1]
        curses.resize_term(height,width)
        names = names_stocks + names_crypto
        prices = prices_stocks + prices_crypto
        elapsed = elapsed_stocks + elapsed_crypto
        table = tabulate([[names[i], prices[i], elapsed[i]] for i in np.arange(len(names))], 
                headers=['Symbol', 'Price', 'max delay[ms]'], showindex="always")
        table_pad.resize(table_height,width)
        table_pad.clear()
        table_pad.addstr(table)
        try:
            global table_pos
            # mysterious +1 needed to make scrolling full screen
            table_pad.refresh(table_pos,0,header_height,0,height-header_height+1,width)
        except:
            pass
        end = time.time()
        elapsed = (end-start)
        if (elapsed<s):
            time.sleep(s-elapsed)

# define function for timing last successful request
def timer(s):
    while (not stop_all):
        start = time.time()
        for i, url in enumerate(URLs_crypto):
            current = time.time()
            elapsed_crypto[i] = int(1000*(current-start_crypto[i]))
        for i, url in enumerate(URLs_stocks):
            current = time.time()
            elapsed_stocks[i] = int(1000*(current-start_stocks[i]))
        end = time.time()
        elapsed = (end-start)
        if (elapsed<s):
            time.sleep(s-elapsed)
           
# define keylistener function
def key_listener():
    while True:  # making a loop
        try:
            key = screen.getkey()
            try:
                if str(key) == 'q':  # if key 'q' is pressed 
                    # notify user of shutdown process
                    title_window.clear()
                    title_window.addstr("Shutting down...\n")
                    title_window.refresh()
                    # wait for all threads to stop
                    global stop_all
                    stop_all = True
                    for i, url in enumerate(URLs_crypto):
                        threads_crypto[i].join()
                    crypto_stocks = []
                    for i, url in enumerate(URLs_stocks):
                        threads_stocks[i].join()
                    # clear screen, reset cursor visibility and close programm
                    clear()
                    curses.curs_set(1)
                    os._exit(1)
            except:
                # don't do anything if non char key was pressed
                pass
            # scroll with up/down buttons
            global table_pos
            try:
                if str(key) == 'KEY_DOWN':
                    if table_pos < num_crypto_URLs+num_stocks_URLs-(height-header_height-2):
                        table_pos += 1
            except:
                pass
            try:
                if str(key) == 'KEY_UP':
                    if table_pos > 0:
                        table_pos -= 1
            except:
                pass
        except:
            pass


# set update frequency for drawing screen and requesting prices
timer_freq = 0.1
drawing_freq = 0.1
update_freq = 5.0

if __name__ == '__main__':
    # initialize threads
    threads_crypto = []
    for i, url in enumerate(URLs_crypto):
        x = threading.Thread(target=getPrice_crypto, args=(url,i,update_freq,))
        threads_crypto.append(x)
        x.start()
    threads_stocks = []
    for i, url in enumerate(URLs_stocks):
        x = threading.Thread(target=getPrice_stocks, args=(url,i,update_freq,))
        threads_stocks.append(x)
        x.start()
    drawing_thread = threading.Thread(target=draw, args=(drawing_freq,))
    drawing_thread.start()
    timer_thread = threading.Thread(target=timer, args=(timer_freq,))
    timer_thread.start()
    key_listener_thread = threading.Thread(target=key_listener, args=())
    key_listener_thread.start()


# setup key listener
#def on_press(key):
#    # exit when q is pressed
#    try:
#        if key.char == 'q':
#            # notify user of shutdown process
#            title_window.clear()
#            title_window.addstr("Shutting down...\n")
#            title_window.refresh()
#            # wait for all threads to stop
#            global stop_all
#            stop_all = True
#            for i, url in enumerate(URLs_crypto):
#                threads_crypto[i].join()
#            crypto_stocks = []
#            for i, url in enumerate(URLs_stocks):
#                threads_stocks[i].join()
#            # clear screen, reset cursor visibility and close programm
#            clear()
#            curses.curs_set(1)
#            os._exit(1)
#    except AttributeError:
#        # don't do anything if non char key was pressed
#        pass
#
#    # scroll with up/down buttons
#    global table_pos
#    try:
#        if key == Key.down:
#            if table_pos < num_crypto_URLs+num_stocks_URLs-(height-header_height-2):
#                table_pos += 1
#    except:
#        pass
#    try:
#        if key == Key.up:
#            if table_pos > 0:
#                table_pos -= 1
#    except:
#        pass
#
#
## Collect events until released
#with Listener(
#        on_press=on_press) as listener:
#    listener.join()






