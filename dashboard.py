import requests
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
#from pyvirtualdisplay import Display
import curses


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
URLs_stocks = []
URLs_stocks.append('https://www.marketwatch.com/investing/stock/gme')
URLs_stocks.append('https://www.marketwatch.com/investing/stock/amc')
URLs_stocks.append('https://www.marketwatch.com/investing/stock/bb')
URLs_stocks.append('https://www.marketwatch.com/investing/stock/xmrusd')
#URL[1] = 'https://coinmarketcap.com/currencies/monero/'
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
#        'referer': 'https://www.coinbase.com'}
#page = requests.get(URL, headers=headers)

clear = lambda: os.system('clear')
size = os.get_terminal_size()
width = size[0]
height = size[1]
def getPrice_crypto(URL):
    page = requests.get(URL)
    
    #print(page)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    price = soup.find(class_=re.compile("^priceValue")).get_text()
    name = soup.find(class_=re.compile("^nameSymbol")).get_text()
    return name, price
    
    #job_elems = results.find_all('section', class_='AssetChartAmount*')
    #job_elems = results.find_all('section', class_=re.compile("^priceValue"))
    #
    #for job_elem in job_elems:
    #        print(job_elem, end='\n'*2)

def getPrice_stocks(URL):
    #display = Display(visible=0, size=(800, 800))  
    #display.start()
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    #options.add_argument('--window-size=640,480')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome('/home/diego/Programming/dashboard/chromedriver', options=options) 
    driver.get(URL)
    page = driver.page_source
    
    #print(page)
    soup = BeautifulSoup(page, 'html.parser')
    
    price = soup.find_all(class_=re.compile("^value$"), field="Last")[0].get_text()
    #print(price)
    name = soup.find(class_="company__ticker").get_text()
    return name, price
    

header_height = 2
screen = curses.initscr()
title_window = curses.newwin(header_height,width,0,0)
crypto_table_pad = curses.newwin(height,int(width/2),header_height,0)
stocks_table_pad = curses.newwin(height,int(width/2),header_height,int(width/2))
title_window.addstr("The Almighty Dashboard \n")
title_window.refresh()
while 1:
    start = time.time()
    names_crypto = []
    prices_crypto = []
    names_stocks = []
    prices_stocks = []
    for url in URLs_crypto:
        name, price = getPrice_crypto(url)
        names_crypto.append(name)
        prices_crypto.append(price)
    for url in URLs_stocks:
        name, price = getPrice_stocks(url)
        names_stocks.append(name)
        prices_stocks.append(price)
    #clear()
    #total_string = ""
    #for i in np.arange(len(names)):
    #    total_string += names[i] + "\n"
    #    total_string += prices[i] + "\n"
    table_crypto = tabulate([[names_crypto[i], prices_crypto[i]] for i in np.arange(len(names_crypto))], 
            headers=['Symbol', 'Price'], showindex="always")
    #table_crypto.title("Crypto Currencies")
    table_stocks = tabulate([[names_stocks[i], "$" + prices_stocks[i]] for i in np.arange(len(names_stocks))], 
        headers=['Symbol', 'Price'], showindex="always")
    #table_stocks.title("Stocks")
    #print("Crypto Currencies")
    #print(table_crypto)
    crypto_table_pad.clear()
    stocks_table_pad.clear()
    crypto_table_pad.addstr(table_crypto)
    stocks_table_pad.addstr(table_stocks)
    crypto_table_pad.refresh()
    stocks_table_pad.refresh()
    #print("\n")
    #print("Stocks")
    #print(table_stocks)
    #print(tw.wrap(total_string, width=width, max_lines=height))
    end = time.time()
    elapsed = (end-start)
    #print("\n")
    #print("time taken to scrape: " + str(elapsed))
    if elapsed < 5.0:
        time.sleep(5.0-elapsed)



