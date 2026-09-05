import json
import subprocess
try:
    from coinbase.wallet.client import Client
except ImportError:
    Client = None

class DataSourceInitializer:
    def __init__(self, path):
        self.monero_wallet_addresses = []
        self.num_monero_wallet_addresses = 0
        self.set_monero_wallet_addresses = False

        self.uphold_token = ""
        self.uphold_cards = []
        self.num_uphold_cards = 0
        self.set_uphold_token = False

        self.coinbase_api_key = ""
        self.coinbase_api_secret = ""
        self.coinbase_currencies = []
        self.num_coinbase_currencies = 0
        self.set_coinbase_api = False

        self.marketwatch_urls = []
        self.num_marketwatch_urls = 0
        self.set_marketwatch_urls = False

        self.coinmarketcap_urls = []
        self.num_coinmarketcap_urls = 0
        self.set_coinmarketcap_urls = False

        self.data_sources_dict = {}
        self.read_json_config(path)

    def read_json_config(self, path):
        with open(path) as json_file:
            data = json.load(json_file)
            if 'monero_wallet_address' in data:
                addr = data['monero_wallet_address']
                if isinstance(addr, list):
                    self.monero_wallet_addresses.extend(addr)
                else:
                    self.monero_wallet_addresses.append(addr)
                self.set_monero_wallet_addresses = True
                self.num_monero_wallet_addresses = len(self.monero_wallet_addresses)
            if 'uphold_token' in data:
                self.uphold_token = data['uphold_token']
                self.set_uphold_token = True
                self.set_uphold_cards()
            if 'coinbase_api_key' in data and 'coinbase_api_secret' in data:
                self.coinbase_api_key = data['coinbase_api_key']
                self.coinbase_api_secret = data['coinbase_api_secret']
                self.set_coinbase_api = True
                self.set_coinbase_currencies()
            if 'marketwatch_urls' in data:
                self.marketwatch_urls = data['marketwatch_urls']
                self.num_marketwatch_urls = len(self.marketwatch_urls)
                self.set_marketwatch_urls = True
            elif 'stock_symbols' in data:
                self.marketwatch_urls = data['stock_symbols']
                self.num_marketwatch_urls = len(self.marketwatch_urls)
                self.set_marketwatch_urls = True
            if 'coinmarketcap_urls' in data:
                self.coinmarketcap_urls = data['coinmarketcap_urls']
                self.num_coinmarketcap_urls = len(self.coinmarketcap_urls)
                self.set_coinmarketcap_urls = True
            elif 'crypto_symbols' in data:
                self.coinmarketcap_urls = data['crypto_symbols']
                self.num_coinmarketcap_urls = len(self.coinmarketcap_urls)
                self.set_coinmarketcap_urls = True

            self.data_sources_dict = {
                "monero_wallet_addresses": self.monero_wallet_addresses,
                "num_monero_wallet_addresses": self.num_monero_wallet_addresses,
                "uphold_token": self.uphold_token,
                "uphold_cards": self.uphold_cards,
                "num_uphold_cards": self.num_uphold_cards,
                "coinbase_api_key": self.coinbase_api_key,
                "coinbase_api_secret": self.coinbase_api_secret,
                "coinbase_currencies": self.coinbase_currencies,
                "num_coinbase_currencies": self.num_coinbase_currencies,
                "marketwatch_urls": self.marketwatch_urls,
                "num_marketwatch_urls": self.num_marketwatch_urls,
                "coinmarketcap_urls": self.coinmarketcap_urls,
                "num_coinmarketcap_urls": self.num_coinmarketcap_urls
            }

    def get_active_data_sources(self):
        return (self.set_monero_wallet_addresses, self.set_uphold_token,
                self.set_coinbase_api, self.set_marketwatch_urls,
                self.set_coinmarketcap_urls)

    def get_data_sources(self):
        return self.data_sources_dict

    def set_uphold_cards(self):
        try:
            bashCommand = ["curl", "-s", "https://api.uphold.com/v0/me/cards",
                           "-H", "Authorization: Bearer " + self.uphold_token]
            process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
            output, error = process.communicate()
            data = json.loads(output.decode("utf-8"))
            if isinstance(data, list):
                for card in data:
                    if float(card.get("balance", 0)) > 0:
                        self.uphold_cards.append(card["currency"])
                        self.num_uphold_cards += 1
        except Exception:
            pass

    def set_coinbase_currencies(self):
        if Client is None:
            return
        try:
            API_KEY = self.coinbase_api_key
            API_SECRET = self.coinbase_api_secret
            client = Client(API_KEY, API_SECRET)
            accounts = client.get_accounts()
            for currency in accounts.get("data", []):
                if float(currency.get("balance", {}).get("amount", 0)) > 0:
                    self.coinbase_currencies.append(currency["balance"]["currency"])
                    self.num_coinbase_currencies += 1
        except Exception:
            pass




