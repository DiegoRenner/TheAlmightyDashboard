import sys
import time
import os
import numpy as np
import curses
import threading
from init_data_sources import DataSourceInitializer
from data_grabbers import DataGrabber
from pynput.keyboard import Key, Listener
import keyboard

if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = "config_no_accounts.json"

dataSourceInitialier = DataSourceInitializer(path)

set_monero_wallet_addresses, set_uphold_token, set_coinbase_api, \
set_marketwatch_urls, set_coinmarketcap_urls = \
    dataSourceInitialier.get_active_data_sources()
data_sources_dict = dataSourceInitialier.data_sources_dict
data_grabber = DataGrabber(data_sources_dict)

num_monero_wallet_addresses = data_sources_dict["num_monero_wallet_addresses"]
monero_wallet_addresses = data_sources_dict["monero_wallet_addresses"]
num_uphold_cards = data_sources_dict["num_uphold_cards"]
uphold_token = data_sources_dict["uphold_token"]
uphold_cards = data_sources_dict["uphold_cards"]
num_coinbase_currencies = data_sources_dict["num_coinbase_currencies"]
coinbase_api_key = data_sources_dict["coinbase_api_key"]
coinbase_api_secret = data_sources_dict["coinbase_api_secret"]
coinbase_currencies = data_sources_dict["coinbase_currencies"]

num_marketwatch_urls = data_sources_dict["num_marketwatch_urls"]
marketwatch_urls = data_sources_dict["marketwatch_urls"]
num_coinmarketcap_urls = data_sources_dict["num_coinmarketcap_urls"]
coinmarketcap_urls = data_sources_dict["coinmarketcap_urls"]

# initialize terminal and header sizes
size = os.get_terminal_size()
width = size[0]
height = size[1]
header_height = 2
table_header_height = 2
column_spacing = 4
max_table_pos = 0

# initialize ncurses screen and windows for the header and tables
screen = curses.initscr()
# prevent getkey() from refreshing automatically
screen.refresh()
# uncomment for non-blocking getkey(), seems to only make the programm less efficient
#screen.nodelay(True)
curses.curs_set(0) # make cursor invisible
# prevent registered input from being output to screen
curses.noecho()
# enable keys like arrow keys to be registered
screen.keypad(True)

title_window = curses.newwin(header_height,width,0,0)
title_window.addstr("The Almighty Dashboard \n")
title_window.refresh()
bg_window = curses.newwin(height,width,0,0)

ticker_table_height = 2+num_marketwatch_urls+num_coinmarketcap_urls
ticker_table_width = int(width/2)
column1_height = height-header_height
column1_width = ticker_table_width+column_spacing
column1_pad = curses.newpad(ticker_table_height, ticker_table_width)

balance_table_height = 2+num_monero_wallet_addresses+num_coinbase_currencies+num_uphold_cards+1
balance_table_width = int(width/2)
column2_height = height-header_height
column2_width = width-column1_width
column2_pad = curses.newpad(height, balance_table_width)

# initialize storage for data
#names_coinmarketcap = ["unloaded"] * num_crypto_URLs
#prices_coinmarketcap = [0.0] * num_crypto_URLs
#elapsed_coinmarketcap = [0.0] * num_crypto_URLs
#start_coinmarketcap = [time.time()] * num_crypto_URLs
#names_marketwatch = ["unloaded"] * num_stocks_URLs
#prices_stoc = [0.0]*num_stocks_URLs
#elapsed_stocks = [0.0]*num_stocks_URLs
#start_stocks = [time.time()]*num_stocks_URLs
#num_owned = 3
#names_owned = ["unloaded"]*num_owned
#names_owned[0] = "XMR"
#names_owned[1] = "BAT"
#outstanding = [0.0]*num_owned
#balance = [0.0]*num_owned
#total = [0.0]*num_owned
#MO_data = ["test"]*2

# initialize flag for orderly stopping of all threads
stop_all=False
# initialize table position for scrolling with arrow keys
table_pos=0
resize_lock = threading.Lock()
# define clear function to clear terminal before exiting
clear = lambda: os.system('clear')

# define functions for scraping links

# define function for drawing screen
def draw(s, threaded=True):
    prev_balance_table_width = 0
    prev_ticker_table_width = 0
    prev_table_pos = 0
    prev_height = 0
    prev_width = 0
    while (not stop_all):
        start = time.time()
        global size, width, height
        if threaded:
            size = os.get_terminal_size()
        width = size[0]
        height = size[1]
        column_width = int(width/2)
        curses.resize_term(height,width)
        ticker_table = data_grabber.get_ticker_table()
        ticker_table_width = int(np.ceil(len(ticker_table)/ticker_table_height))
        balance_table = data_grabber.get_balance_table()
        balance_table_widths = [balance_table.rsplit("\n")[i].__len__() for i in np.arange(len(balance_table.rsplit("\n")))]
        balance_table_width = max(balance_table_widths)+1
        #balance_table_width = balance_table.rsplit("\n")[0].__len__()+1
        ticker_table_widths = [ticker_table.rsplit("\n")[i].__len__() for i in np.arange(len(ticker_table.rsplit("\n")))]
        ticker_table_width = max(ticker_table_widths)+1
        #ticker_table_width = ticker_table.rsplit("\n")[0].__len__()+1

        #print(balance_table)
        #print(balance_table_widths)
        #print(balance_table_width)

        if(not threaded):
            break
        #try:
        #except:
       #     pass
        drawing_width = balance_table_width+ticker_table_width+column_spacing
        #try:
        ticker_table_draw_height = ticker_table_height + header_height
        if ticker_table_height + header_height >= height:
            ticker_table_draw_height = height-1
        balance_table_draw_height = balance_table_height + header_height
        if balance_table_height + header_height >= height:
            balance_table_draw_height = height-1


        min_width = max(ticker_table_width, balance_table_width)
        min_height = header_height
        global table_pos
        global max_table_pos
        # mysterious +1 needed to make scrolling full screen
        #if prev_ticker_table_width != ticker_table_width or prev_balance_table_width != balance    _tab#le_width or prev_table_pos != table_pos or prev_width != width or prev_height != height:
        #    #screen.clear()
        #    #screen.refresh()
        #    bg_window.clear()
        #    bg_window.refresh()
        #    title_window.clear()
        #    title_window.addstr("The Almighty Dashboard \n")
        #    title_window.refresh()
        if drawing_width < width and min_height < height:
            column1_height = height - header_height
            column1_width = ticker_table_width + column_spacing
            column2_height = height - header_height
            column2_width = width - column1_width
            # multiply by two so that no leftovers stay on screen
            column1_height = 2*max(height - header_height, ticker_table_height)
            #column1_width = max(ticker_table_width + column_spacing,ticker_table_width)
            column2_height = 2*max(height - header_height, balance_table_height)
            #column2_width = max(width - column1_width, ticker_table_width)

            #add -1 for tolerance when resizing
            column1_bottom = height-1
            #column1_bottom = max(height, header_height+ticker_table_height+1)
            column1_right = ticker_table_width + column_spacing
            column2_bottom = height-1
            #column2_bottom = max(height, header_height+balance_table_height+1)
            column2_right = width

            column1_pad.resize(column1_height, column1_width)
            column1_pad.clear()
            column1_pad.addstr(ticker_table)

            column2_pad.resize(column2_height, column2_width)
            column2_pad.clear()
            column2_pad.addstr(balance_table)

            title_window.resize(header_height,width)
            title_window.clear()
            title_window.addstr("The Almighty Dashboard \n")
            title_window.refresh()
            try:
                column1_pad.refresh(min(table_pos, ticker_table_height), 0, header_height, 0, column1_bottom, column1_right)
                column2_pad.refresh(min(table_pos, balance_table_height), 0, header_height, column1_right, column2_bottom, column2_right)
            except:
                pass
            max_table_pos = max(ticker_table_height,balance_table_height)+header_height-height if max(ticker_table_height,balance_table_height)+header_height > height else 0
        elif min_width < width and min_height < height:
            title_window.resize(header_height,width)
            title_window.clear()
            title_window.addstr("The Almighty Dashboard \n")
            title_window.refresh()
            table_height = ticker_table_height + balance_table_height + 1
            # multiply by two so that no leftovers stay on screen
            column1_height = 2*max(height - header_height, table_height)
            column1_width = width
            column2_height = 0
            column2_width = 0
            #column1_height = max(height - header_height,table_height)
            #column1_width = max(width, ticker_table_width, balance_table_width)
            #column2_height = 0
            #column2_width = 0

            #add -1 for tolerance when resizing
            column1_bottom = height-1
            column1_right = width
            column2_bottom = 0
            column2_right = 0
            column1_pad.resize(column1_height, column1_width)
            column1_pad.clear()
            column1_pad.addstr(ticker_table + "\n\n" + balance_table)
            try:
                column1_pad.refresh(min(table_pos, table_height), 0, header_height, 0, column1_bottom, column1_right)
            except:
                pass
            max_table_pos = table_height+header_height-height if table_height > height else 0
        else:
            title_window.resize(height, width)
            title_window.clear()
            title_window.addstr("make biggr pls")
            title_window.refresh()
            max_table_pos = 0
            #balance_table_pad.refresh(table_pos,0,header_height+ticker_table_height-table_pos,0,balance_table_draw_height,drawing_width)

            prev_table_pos = table_pos
            prev_width = width
            prev_height = height
            #except:
            #    pass
        prev_balance_table_width = balance_table_width
        prev_ticker_table_width = ticker_table_width
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
                    data_grabber.stop_all = True
                    #for i, url in enumerate(num_coinmarketcap_urls):
                    #    threads_crypto[i].join()
                    #crypto_stocks = []
                    #for i, url in enumerate(num_marketwatch_urls):
                    #    threads_stocks[i].join()
                    # clear screen, reset cursor visibility and close programm
                    clear()
                    curses.curs_set(1)
                    os._exit(1)
            except:
                # don't do anything if non char key was pressed
                pass
            # scroll with up/down buttons
            #with resize_lock:
            global table_pos
            try:
                if str(key) == 'KEY_DOWN' or str(key) =='j':
                    #if table_pos < num_coinmarketcap_urls+\
                    #        num_marketwatch_urls-(height-header_height-2):
                    global max_table_pos
                    if table_pos < max_table_pos:
                        table_pos += 1
            except:
                pass
            try:
                if str(key) == 'KEY_UP' or str(key) == 'k':
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
    for i, url in enumerate(coinmarketcap_urls):
        x = threading.Thread(target=data_grabber.getPrice_coinmarketcap, args=(url,i,update_freq,))
        threads_crypto.append(x)
        x.start()
    threads_stocks = []
    for i, url in enumerate(marketwatch_urls):
        x = threading.Thread(target=data_grabber.getPrice_marketwatch, args=(url,i,update_freq,))
        threads_stocks.append(x)
        x.start()
    threads_monero_wallets = []
    for i, monero_wallet_address in enumerate(monero_wallet_addresses):
        x = threading.Thread(target=data_grabber.setData_MO, args=(monero_wallet_address,i,update_freq,))
        threads_monero_wallets.append(x)
        x.start()
    threads_uphold_cards = []
    for i, uphold_card in enumerate(uphold_cards):
        x = threading.Thread(target=data_grabber.setData_Uphold, args=(uphold_token,uphold_card,i,update_freq,))
        threads_uphold_cards.append(x)
        x.start()
    Coinbase_data_thread = threading.Thread(target=data_grabber.setData_Coinbase, args=(coinbase_api_key, coinbase_api_secret, update_freq,))
    Coinbase_data_thread.start()
    drawing_thread = threading.Thread(target=draw, args=(drawing_freq,))
    drawing_thread.start()
    timer_thread = threading.Thread(target=data_grabber.timer, args=(timer_freq,))
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
## Collect events until released
#with Listener(
#        on_press=on_press) as listener:
#    listener.join()






