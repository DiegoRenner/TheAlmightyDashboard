import unittest
import time
import threading
import numpy as np
from init_data_sources import DataSourceInitializer
from data_grabbers import DataGrabber
#from dashboard_threaded import draw


class MyTestCase(unittest.TestCase):
    dataSourceInitializer = DataSourceInitializer("config.json")
    data_sources_dict = dataSourceInitializer.get_data_sources()
    data_grabber = DataGrabber(data_sources_dict)
    num_marketwatch_urls = data_sources_dict["num_marketwatch_urls"]
    marketwatch_urls = data_sources_dict["marketwatch_urls"]
    num_coinmarketcap_urls = data_sources_dict["num_coinmarketcap_urls"]
    coinmarketcap_urls = data_sources_dict["coinmarketcap_urls"]
    num_monero_wallet_addresses = data_sources_dict["num_monero_wallet_addresses"]
    monero_wallet_addresses = data_sources_dict["monero_wallet_addresses"]
    num_uphold_cards = data_sources_dict["num_uphold_cards"]
    uphold_token = data_sources_dict["uphold_token"]
    uphold_cards = data_sources_dict["uphold_cards"]
    num_coinbase_currencies = data_sources_dict["num_coinbase_currencies"]
    coinbase_api_key = data_sources_dict["coinbase_api_key"]
    coinbase_api_secret = data_sources_dict["coinbase_api_secret"]
    coinbase_currencies = data_sources_dict["coinbase_currencies"]
    update_freq = 5.0

    def test_data_threads(self):
        print(self.marketwatch_urls)
        print(self.coinmarketcap_urls)
        threads_crypto = []
        for i, url in enumerate(self.coinmarketcap_urls):
            x = threading.Thread(target=self.data_grabber.getPrice_coinmarketcap, args=(url, i, self.update_freq,))
            threads_crypto.append(x)
            x.start()
        threads_stocks = []
        for i, url in enumerate(self.marketwatch_urls):
            x = threading.Thread(target=self.data_grabber.getPrice_marketwatch, args=(url, i, self.update_freq,))
            threads_stocks.append(x)
            x.start()
        threads_monero_wallets = []
        for i, monero_wallet_address in enumerate(self.monero_wallet_addresses):
            x = threading.Thread(target=self.data_grabber.setData_MO, args=(monero_wallet_address, i, self.update_freq,))
            threads_monero_wallets.append(x)
            x.start()
        threads_uphold_cards = []
        for i, uphold_card in enumerate(self.uphold_cards):
            x = threading.Thread(target=self.data_grabber.setData_Uphold, args=(self.uphold_token, uphold_card, i, self.update_freq,))
            threads_uphold_cards.append(x)
            x.start()
        Coinbase_data_thread = threading.Thread(target=self.data_grabber.setData_Coinbase,
                                                args=(self.coinbase_api_key, self.coinbase_api_secret, self.update_freq,))
        Coinbase_data_thread.start()
        time.sleep(5)
        print(self.data_grabber.get_ticker_table())
        print(self.data_grabber.get_balance_table().rsplit("\n")[1].__len__())
        balance_table_widths = [self.data_grabber.get_balance_table().rsplit("\n")[i].__len__() for i in np.arange(len(self.data_grabber.get_balance_table().rsplit("\n")))]
        print(max(balance_table_widths))
        print(self.data_grabber.names_coinmarketcap)
        #print(self.data_grabber.get_ticker_table())

    def test_drawing_thread(self):
        draw(0.5, False)



if __name__ == '__main__':
    unittest.main()
