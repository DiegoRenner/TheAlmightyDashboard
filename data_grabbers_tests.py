import os
import unittest
import numpy as np
from init_data_sources import DataSourceInitializer
from data_grabbers import DataGrabber


class MyTestCase(unittest.TestCase):
    config_path = "config.json" if os.path.exists("config.json") else "config_no_accounts.json"
    dataSourceInitializer = DataSourceInitializer(config_path)
    data_sources_dict = dataSourceInitializer.get_data_sources()
    dataGrabber = DataGrabber(data_sources_dict)

    def test_getPrice_crypto(self):
        if self.data_sources_dict["num_coinmarketcap_urls"] > 0:
            url = self.data_sources_dict["coinmarketcap_urls"][0]
            self.dataGrabber.getPrice_coinmarketcap(url, 0, 1, threaded=False)
            self.assertNotEqual(self.dataGrabber.prices_coinmarketcap[0], "FAILED")
            self.assertNotEqual(self.dataGrabber.names_coinmarketcap[0], "unloaded")

    def test_getPrice_stock(self):
        if self.data_sources_dict["num_marketwatch_urls"] > 0:
            url = "GME"
            self.dataGrabber.getPrice_marketwatch(url, 0, 1, threaded=False)
            self.assertEqual(self.dataGrabber.names_marketwatch[0], "GME")
            self.assertIsInstance(self.dataGrabber.prices_marketwatch[0], float)

    def test_setData_MO(self):
        num = self.data_sources_dict.get("num_monero_wallet_addresses", 0)
        for i in np.arange(num):
            self.dataGrabber.setData_MO(
                self.data_sources_dict["monero_wallet_addresses"][i], i, 1, False)
        for i in np.arange(num):
            print(self.dataGrabber.balance_monero_wallets[i])
            print(self.dataGrabber.names_monero_wallets[i])
        self.assertEqual(True, True)

    def test_setData_Uphold(self):
        num = self.data_sources_dict.get("num_uphold_cards", 0)
        for i in np.arange(num):
            self.dataGrabber.setData_Uphold(
                self.data_sources_dict["uphold_token"],
                self.data_sources_dict["uphold_cards"][i], i, 1, False)
        for i in np.arange(num):
            print(self.dataGrabber.balance_uphold_cards[i])
            print(self.dataGrabber.names_uphold_cards[i])
        self.assertEqual(True, True)

    def test_setData_Coinbase(self):
        num = self.data_sources_dict.get("num_coinbase_currencies", 0)
        if num > 0:
            self.dataGrabber.setData_Coinbase(
                self.data_sources_dict["coinbase_api_key"],
                self.data_sources_dict["coinbase_api_secret"], 1, False)
        for i in np.arange(num):
            print(self.dataGrabber.balance_coinbase_currencies[i])
            print(self.dataGrabber.names_coinbase_currencies[i])
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
