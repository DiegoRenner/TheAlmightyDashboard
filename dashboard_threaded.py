import requests_html
from bs4 import BeautifulSoup
import re
import time
import os
import numpy as np
from termcolor import colored
import textwrap as tw
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import curses
import threading
from pynput.keyboard import Key, Listener

# initialize links to scrape
URLs_crypto = []
URLs_crypto.append('https://coinmarketcap.com/currencies/bitcoin/')
URLs_crypto.append('https://coinmarketcap.com/currencies/ethereum/')
URLs_crypto.append('https://coinmarketcap.com/currencies/monero/')
URLs_crypto.append('https://coinmarketcap.com/currencies/basic-attention-token/')
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

# initialize terminal size
size = os.get_terminal_size()
width = size[0]
height = size[1]
header_height = 2

# initialize ncurses screen and windows for the header and tables
screen = curses.initscr()
curses.curs_set(0) # make cursor invisible
title_window = curses.newwin(header_height,width,0,0)
crypto_table_pad = curses.newwin(height,int(width/2),header_height,0)
stocks_table_pad = curses.newwin(height,int(width/2),header_height,int(width/2))
title_window.addstr("The Almighty Dashboard \n")
title_window.refresh()

# initialize storage for data
names_crypto = ["unloaded"]*num_crypto_URLs
prices_crypto = [0.0]*num_crypto_URLs
elapsed_crypto = [0.0]*num_crypto_URLs
names_stocks = ["unloaded"]*num_stocks_URLs
prices_stocks = [0.0]*num_stocks_URLs
elapsed_stocks = [0.0]*num_stocks_URLs

# initialize flag for orderly stopping of all threads
stop_all=False

# define functions for scraping links
def getPrice_crypto(URL,i,s):
    while (not stop_all):
        start = time.time()
        session = requests_html.HTMLSession()
        page = session.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        price = soup.find(class_=re.compile("^priceValue")).get_text()
        name = soup.find(class_=re.compile("^nameSymbol")).get_text()
        prices_crypto[i] = price
        names_crypto[i] = name
        end = time.time()
        elapsed = (end-start)
        if (elapsed<s):
            time.sleep(s-elapsed)

def getPrice_stocks(URL,i,s):
    while (not stop_all):
        start = time.time()
        #options = webdriver.ChromeOptions()
        #options.add_argument('--no-sandbox')
        #options.add_argument('--headless')
        #options.add_argument('--disable-gpu')
        #driver = webdriver.Chrome('/home/diego/Programming/dashboard/chromedriver', options=options) 
        #driver.get(URL)
        #page = driver.page_source
        #driver.close()
        #driver.quit()
        session = requests_html.HTMLSession()
        page = session.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        price = soup.find_all(class_=re.compile("^value$"), field="Last")[0].get_text()
        #print(soup.find_all(class_=re.compile("^value$")))
        name = soup.find(class_="company__ticker").get_text()
        names_stocks[i] = name
        prices_stocks[i] = price
        end = time.time()
        elapsed = (end-start)
        if (elapsed<s):
            time.sleep(s-elapsed)

# define functions for drawing screen
def draw(s):
    while 1:
        start = time.time()
        size = os.get_terminal_size()
        width = size[0]
        height = size[1]
        crypto_table_pad = curses.newwin(height,int(width/2),header_height,0)
        stocks_table_pad = curses.newwin(height,int(width/2),header_height,int(width/2))
        table_crypto = tabulate([[names_crypto[i], prices_crypto[i], time.time()-elapsed_crypto[i] if elapsed_crypto[i] > 0.0 else 0.0] for i in np.arange(len(names_crypto))], 
                headers=['Symbol', 'Price', 'Requested [s] ago'], showindex="always")
        table_stocks = tabulate([[names_stocks[i], "$" + str(prices_stocks[i]), time.time()-elapsed_stocks[i] if elapsed_stocks[i] > 0.0 else 0.0] for i in np.arange(len(names_stocks))], 
                headers=['Symbol', 'Price', 'Requested [s] ago'], showindex="always")
        crypto_table_pad.clear()
        crypto_table_pad.addstr(table_crypto)
        crypto_table_pad.refresh()
        stocks_table_pad.clear()
        stocks_table_pad.addstr(table_stocks)
        stocks_table_pad.refresh()
        end = time.time()
        elapsed = (end-start)
        if (elapsed<s):
            time.sleep(s-elapsed)

# set update frequency for drawing screen and requesting prices
drawing_freq = 0.5
update_freq = 5.0

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
#key_listener_thread = threading.Thread(target=key_listener, args=())
#key_listener_thread.start()

# define clear function to clear terminal before exiting
clear = lambda: os.system('clear')

# define functions key presses
def on_press(key):
    try:
        if key.char == 'q':
            title_window.clear()
            title_window.addstr("Shutting down...\n")
            title_window.refresh()
            global stop_all
            stop_all = True
            for i, url in enumerate(URLs_crypto):
                threads_crypto[i].join()
            crypto_stocks = []
            for i, url in enumerate(URLs_stocks):
                threads_stocks[i].join()
            clear()
            # Stop listener
            curses.curs_set(1) # reset cursor visibility
            os._exit(1)
    except AttributeError:
        flag = 0
# Collect events until released
with Listener(
        on_press=on_press) as listener:
    listener.join()

#def key_listener():
#    while True:  # making a loop
#        try:  # used try so that if user pressed other than the given key error will not be shown
#            if keyboard.is_pressed('q'):  # if key 'q' is pressed 
#                print("test")
#                os._exit(1)
#        except:
#            test = 0  # if user pressed a key other than the given key the l





