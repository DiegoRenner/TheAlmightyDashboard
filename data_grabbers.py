import requests
import numpy as np
from bs4 import BeautifulSoup
import time
import json
import subprocess
import re
from tabulate import tabulate

try:
    from monero.wallet import Wallet
    from monero.backends.jsonrpc import JSONRPCWallet
except ImportError:
    Wallet = None
    JSONRPCWallet = None

try:
    from coinbase.wallet.client import Client
except ImportError:
    Client = None

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

    def getPrice_coinmarketcap(self, URL, i, s, threaded=True):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        slug = URL.strip('/').split('/')[-1].lower() if '/' in URL else URL.strip().lower()
        while (not self.stop_all):
            start = time.time()
            found = False

            # 1. Try CoinMarketCap __NEXT_DATA__
            try:
                page = requests.get(URL, headers=headers, timeout=10)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.content, 'html.parser')
                    next_script = soup.find('script', id='__NEXT_DATA__')
                    if next_script and next_script.string:
                        data = json.loads(next_script.string)
                        detail = data.get('props', {}).get('pageProps', {}).get('detailRes', {}).get('detail', {})
                        symbol = detail.get('symbol')
                        price = detail.get('statistics', {}).get('price')
                        if symbol and price is not None:
                            self.names_coinmarketcap[i] = symbol
                            self.prices_coinmarketcap[i] = float(price)
                            self.start_coinmarketcap[i] = start
                            found = True
            except Exception:
                pass

            # 2. Fallback: CoinGecko simple price
            if not found:
                try:
                    cg_url = f'https://api.coingecko.com/api/v3/simple/price?ids={slug}&vs_currencies=usd'
                    page = requests.get(cg_url, headers=headers, timeout=5)
                    if page.status_code == 200:
                        cg_data = page.json()
                        if slug in cg_data and 'usd' in cg_data[slug] and cg_data[slug]['usd'] is not None:
                            self.names_coinmarketcap[i] = slug.upper()
                            self.prices_coinmarketcap[i] = float(cg_data[slug]['usd'])
                            self.start_coinmarketcap[i] = start
                            found = True
                except Exception:
                    pass

            # 3. Fallback: Yahoo Finance crypto chart
            if not found:
                try:
                    yf_url = f'https://query1.finance.yahoo.com/v8/finance/chart/{slug.upper()}-USD'
                    page = requests.get(yf_url, headers=headers, timeout=5)
                    if page.status_code == 200:
                        yf_data = page.json()
                        result = yf_data.get('chart', {}).get('result')
                        if result:
                            price = result[0].get('meta', {}).get('regularMarketPrice')
                            if price is not None:
                                self.names_coinmarketcap[i] = slug.upper()
                                self.prices_coinmarketcap[i] = float(price)
                                self.start_coinmarketcap[i] = start
                                found = True
                except Exception:
                    pass

            if not found:
                self.names_coinmarketcap[i] = slug.upper()
                self.prices_coinmarketcap[i] = "FAILED"

            if not threaded:
                break
            end = time.time()
            elapsed = (end - start)
            if (elapsed < s):
                time.sleep(s - elapsed)


    def getPrice_marketwatch(self, URL, i, s, threaded=True):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        if '/' in URL:
            ticker = URL.strip('/').split('/')[-1].upper()
        else:
            ticker = URL.strip().upper()

        candidates = [ticker]
        if ticker.endswith('USD') and '-' not in ticker and len(ticker) > 3:
            candidates = [f"{ticker[:-3]}-USD", ticker]

        hosts = ['query1.finance.yahoo.com', 'query2.finance.yahoo.com']

        while (not self.stop_all):
            start = time.time()
            found = False
            delisted = False

            for sym in candidates:
                if found:
                    break
                for host in hosts:
                    try:
                        yf_url = f'https://{host}/v8/finance/chart/{sym}'
                        page = requests.get(yf_url, headers=headers, timeout=8)
                        if page.status_code == 200:
                            data = page.json()
                            result = data.get('chart', {}).get('result')
                            if result:
                                meta = result[0].get('meta', {})
                                price = meta.get('regularMarketPrice')
                                symbol = meta.get('symbol', ticker)
                                if price is not None:
                                    self.names_marketwatch[i] = symbol
                                    self.prices_marketwatch[i] = float(price)
                                    self.start_marketwatch[i] = start
                                    found = True
                                    delisted = False
                                    break
                        elif page.status_code == 404:
                            delisted = True
                            break
                        elif page.status_code == 429:
                            continue
                    except Exception:
                        pass

            if not found:
                self.names_marketwatch[i] = ticker
                self.prices_marketwatch[i] = "DELISTED" if delisted else "FAILED"

            if not threaded:
                break
            end = time.time()
            elapsed = (end - start)
            if (elapsed < s):
                time.sleep(s - elapsed)


    def setData_MO(self, monero_wallet_address, i, s, threaded=True):
        while (not self.stop_all):
            start = time.time()

            try:
                page = requests.get(
                    'https://api.moneroocean.stream/miner/' + monero_wallet_address + '/stats',
                    timeout=5)
                amt_due = float(page.json().get('amtDue', 0)) / 1000000000000
                local_bal = 0.0
                if Wallet is not None and JSONRPCWallet is not None:
                    try:
                        w = Wallet(JSONRPCWallet(port=28088))
                        local_bal = float(w.balance())
                    except Exception:
                        pass
                balance = amt_due + local_bal
                self.balance_monero_wallets[i] = balance
                self.names_monero_wallets[i] = "XMR"
                xmr_price = 0.0
                if "XMR" in self.names_coinmarketcap:
                    idx = self.names_coinmarketcap.index("XMR")
                    p = self.prices_coinmarketcap[idx]
                    if isinstance(p, (int, float)):
                        xmr_price = p
                self.values_monero_wallets[i] = xmr_price * balance
            except Exception:
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
                bashCommand = ["curl", "-s", "https://api.uphold.com/v0/me/cards?q=currency:" + uphold_card + "%20settings.starred:true",
                               "-H", "Authorization: Bearer " + uphold_token]
                process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
                output, error = process.communicate()
                data = json.loads(output.decode("utf-8"))
                card_obj = data[0] if isinstance(data, list) and len(data) > 0 else (data if isinstance(data, dict) else {})
                balance = float(card_obj.get("balance", 0))
                self.balance_uphold_cards[i] = balance
                self.names_uphold_cards[i] = uphold_card
                if uphold_card == "USD":
                    self.values_uphold_cards[i] = balance
                else:
                    coin_price = 0.0
                    if uphold_card in self.names_coinmarketcap:
                        idx = self.names_coinmarketcap.index(uphold_card)
                        p = self.prices_coinmarketcap[idx]
                        if isinstance(p, (int, float)):
                            coin_price = p
                    self.values_uphold_cards[i] = coin_price * balance
                if not threaded:
                    break
            except Exception:
                pass

            end = time.time()
            elapsed = (end - start)
            if (elapsed < s):
                time.sleep(s - elapsed)

    def setData_Coinbase(self, coinbase_api_key, coinbase_api_secret, s, threaded=True):
        while (not self.stop_all):
            start = time.time()
            try:
                if Client is not None and coinbase_api_key and coinbase_api_secret:
                    API_KEY = coinbase_api_key
                    API_SECRET = coinbase_api_secret
                    client = Client(API_KEY, API_SECRET)
                    accounts = client.get_accounts()

                    i = 0
                    for currency in accounts.get("data", []):
                        amt = float(currency.get("balance", {}).get("amount", 0))
                        if amt > 0 and i < len(self.names_coinbase_currencies):
                            self.names_coinbase_currencies[i] = currency["balance"]["currency"]
                            self.balance_coinbase_currencies[i] = amt
                            self.values_coinbase_currencies[i] = float(currency.get("native_balance", {}).get("amount", 0))
                            i += 1
                if not threaded:
                    break
            except Exception:
                pass
            end = time.time()
            elapsed = (end - start)
            if (elapsed < s):
                time.sleep(s - elapsed)
