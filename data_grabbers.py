import requests_html
import numpy as np
from bs4 import BeautifulSoup
import time
import json
from monero.wallet import Wallet
from monero.backends.jsonrpc import JSONRPCWallet
from coinbase.wallet.client import Client
import subprocess
import re
from tabulate import tabulate

class DataGrabber():
    stop_all = False

    num_monero_wallet_addresses = 0
    num_uphold_cards = 0
    num_coinbase_currencies = 0
    num_marketwatch_urls = 0
    num_coinmarketcap_urls = 0

    balance_monero_wallets = []
    values_monero_wallets = []
    names_monero_wallets = []
    balance_uphold_cards = []
    values_uphold_cards = []
    names_uphold_cards = []
    balance_coinbase_currencies = []
    values_coinbase_currencies = []
    names_coinbase_currencies = []

    prices_coinmarketcap = []
    names_coinmarketcap = []
    start_coinmarketcap = []
    elapsed_coinmarketcap = []
    num_coinmarketcap_urls = 0
    prices_marketwatch = []
    names_marketwatch = []
    start_marketwatch = []
    elapsed_marketwatch = []
    num_marketwatch_urls = 0

    def __init__(self, data_sources_dict):
        self.balance_monero_wallets = [0.0]*data_sources_dict["num_monero_wallet_addresses"]
        self.values_monero_wallets = [0.0]*data_sources_dict["num_monero_wallet_addresses"]
        self.names_monero_wallets = [0.0]*data_sources_dict["num_monero_wallet_addresses"]
        self.num_monero_wallet_addresses = data_sources_dict["num_monero_wallet_addresses"]
        self.balance_uphold_cards = [0.0]*data_sources_dict["num_uphold_cards"]
        self.values_uphold_cards = [0.0]*data_sources_dict["num_uphold_cards"]
        self.names_uphold_cards = [0.0]*data_sources_dict["num_uphold_cards"]
        self.num_uphold_cards = data_sources_dict["num_uphold_cards"]
        self.balance_coinbase_currencies = [0.0]*data_sources_dict["num_coinbase_currencies"]
        self.values_coinbase_currencies = [0.0]*data_sources_dict["num_coinbase_currencies"]
        self.names_coinbase_currencies = [0.0]*data_sources_dict["num_coinbase_currencies"]
        self.num_coinbase_currencies = data_sources_dict["num_coinbase_currencies"]

        self.prices_coinmarketcap = [0.0]*data_sources_dict["num_coinmarketcap_urls"]
        self.names_coinmarketcap = ["unloaded"]*data_sources_dict["num_coinmarketcap_urls"]
        self.start_coinmarketcap = [time.time()]*data_sources_dict["num_coinmarketcap_urls"]
        self.elapsed_coinmarketcap = [0.0]*data_sources_dict["num_coinmarketcap_urls"]
        self.num_coinmarketcap_urls = data_sources_dict["num_coinmarketcap_urls"]
        self.prices_marketwatch = [0.0]*data_sources_dict["num_marketwatch_urls"]
        self.names_marketwatch = ["unloaded"]*data_sources_dict["num_marketwatch_urls"]
        self.start_marketwatch = [time.time()]*data_sources_dict["num_marketwatch_urls"]
        self.elapsed_marketwatch = [0.0]*data_sources_dict["num_marketwatch_urls"]
        self.num_marketwatch_urls = data_sources_dict["num_marketwatch_urls"]

    def get_ticker_table(self):
        prices = self.prices_marketwatch + self.prices_coinmarketcap
        names = self.names_marketwatch + self.names_coinmarketcap
        elapsed = self.elapsed_marketwatch + self.elapsed_coinmarketcap
        
        num_tickers = len(names)
        indices = np.arange(1,num_tickers+1)
        indices = indices.tolist()

        table = tabulate([[names[i], prices[i], elapsed[i]] for i in np.arange(num_tickers)],
                         headers=['Symbol', 'Price [$]', 'Delay [ms]'], showindex=indices)
        return table

    def get_balance_table(self):
        balances = self.balance_monero_wallets + \
                   self.balance_uphold_cards + \
                   self.balance_coinbase_currencies
        balances.append("")
        values = self.values_monero_wallets + \
                   self.values_uphold_cards + \
                   self.values_coinbase_currencies
        values.append(sum(values))
        names = self.names_monero_wallets + \
                self.names_uphold_cards + \
                self.names_coinbase_currencies
        names.append("total")
        num_balances = self.num_monero_wallet_addresses + \
                       self.num_uphold_cards + \
                       self.num_coinbase_currencies + 1
        indices = np.arange(1,num_balances)
        indices = indices.tolist()
        indices.append("")
        table = tabulate([[names[i], balances[i], values[i]]for i in np.arange(num_balances)],
                               headers=['Symbol', 'Amount', " Value [$]"], showindex=indices)
        return table

    # define function for timing last successful request
    def timer(self,s):
        while (not self.stop_all):
            start = time.time()
            for i in np.arange(self.num_coinmarketcap_urls):
                self.elapsed_coinmarketcap[i] = int(1000*(time.time()-self.start_coinmarketcap[i]))
            for i in np.arange(self.num_marketwatch_urls):
                self.elapsed_marketwatch[i] = int(1000*(time.time()-self.start_marketwatch[i]))
            end = time.time()
            elapsed = (end-start)
            if (elapsed<s):
                time.sleep(s-elapsed)

    def getPrice_coinmarketcap(self, URL, i, s):
        while (not self.stop_all):
            start = time.time()

            try:
                session = requests_html.HTMLSession()
                page = session.get(URL)
                soup = BeautifulSoup(page.content, 'html.parser')
                price = soup.find(class_=re.compile("^priceValue")).get_text()
                name = soup.find(class_=re.compile("^nameSymbol")).get_text()
                self.prices_coinmarketcap[i] = float(price.replace("$","").replace(",",""))
                self.names_coinmarketcap[i] = name
                self.start_coinmarketcap[i] = start
            except:
                self.prices_coinmarketcap[i] = "FAILED"

            end = time.time()
            elapsed = (end - start)
            if (elapsed < s):
                time.sleep(s - elapsed)


    def getPrice_marketwatch(self, URL, i, s):
        while (not self.stop_all):
            start = time.time()

            try:
                session = requests_html.HTMLSession()
                page = session.get(URL)
                soup = BeautifulSoup(page.content, 'html.parser')
                price = soup.find_all(class_=re.compile("^value$"), field="Last")[0].get_text()
                name = soup.find(class_="company__ticker").get_text()
                self.prices_marketwatch[i] = float(price.replace("$","").replace(",",""))
                self.names_marketwatch[i] = name
                self.start_marketwatch[i] = start
            except:
                self.prices_marketwatch[i] = "FAILED"

            end = time.time()
            elapsed = (end - start)
            if (elapsed < s):
                time.sleep(s - elapsed)


    def setData_MO(self, monero_wallet_address, i, s, threaded=True):
        while (not self.stop_all):
            start = time.time()

            try:
                session = requests_html.HTMLSession()
                page = session.get(
                    'https://api.moneroocean.stream/miner/' + monero_wallet_address + '/stats')
                w = Wallet(JSONRPCWallet(port=28088))
                balance = float(page.json()['amtDue']) / 1000000000000 + float(w.balance())
                self.balance_monero_wallets[i] = balance
                self.names_monero_wallets[i] = "XMR"
                self.values_monero_wallets[i] = self.prices_coinmarketcap[self.names_coinmarketcap.index("XMR")]*balance
            except:
                pass

            if not threaded:
                break
            end = time.time()
            elapsed = (end - start)
            if (elapsed < s):
                time.sleep(s - elapsed)


    def setData_Uphold(self, uphold_token, uphold_card, i, s, threaded=True):
        while (not self.stop_all):
            start = time.time()

            try:
                # headers = {"Authorization":"Bearer <bearer>"}
                # session = requests_html.HTMLSession()
                # page = session.get("https://api.uphold.com/v0/me/cards?q=currency:BAT%20settings.starred:true", headers=headers)
                bashCommand = ["curl", "-s", "https://api.uphold.com/v0/me/cards?q=currency:" + uphold_card + "%20settings.starred:true",
                               "-H", "Authorization: Bearer " + uphold_token]
                process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
                output, error = process.communicate()
                balance = float(json.loads(output.decode("utf-8")[1:-1])["balance"])
                self.balance_uphold_cards[i] = balance
                self.names_uphold_cards[i] = uphold_card
                if uphold_card == "USD":
                    self.values_uphold_cards[i] = balance
                else:
                    self.values_uphold_cards[i] = self.prices_coinmarketcap[self.names_coinmarketcap.index(uphold_card)]*balance
                if not threaded:
                    break
            except:
                pass

            end = time.time()
            elapsed = (end - start)
            if (elapsed < s):
                time.sleep(s - elapsed)

    def setData_Coinbase(self, coinbase_api_key, coinbase_api_secret, s, threaded=True):
        while (not self.stop_all):
            start = time.time()
            try:
                API_KEY = coinbase_api_key
                API_SECRET = coinbase_api_secret
                client = Client(API_KEY, API_SECRET)
                accounts = client.get_accounts()

                i = 0
                for currency in accounts["data"]:
                    if float(currency["balance"]["amount"]) > 0:
                        self.names_coinbase_currencies[i] = currency["balance"]["currency"]
                        self.balance_coinbase_currencies[i] = float(currency["balance"]["amount"])
                        self.values_coinbase_currencies[i] = float(currency["native_balance"]["amount"])
                        i += 1
                if not threaded:
                    break
            except:
                pass
            end = time.time()
            elapsed = (end - start)
            if (elapsed < s):
                time.sleep(s - elapsed)
