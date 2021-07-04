import unittest
import numpy as np
from init_data_sources import DataSourceInitializer
from data_grabbers import DataGrabber


class MyTestCase(unittest.TestCase):
    dataSourceInitializer = DataSourceInitializer("config.json")
    data_sources_dict = dataSourceInitializer.get_data_sources()
    dataGrabber = DataGrabber(data_sources_dict)
    def test_setData_MO(self):
        for i in np.arange(self.data_sources_dict["num_monero_wallet_adresses"]):
            self.dataGrabber.setData_MO(
                self.data_sources_dict["monero_wallet_adress"][i],i,1,False)
        for i in np.arange(self.data_sources_dict["num_monero_wallet_adresses"]):
            print(self.dataGrabber.balance_monero_wallets[i])
            print(self.dataGrabber.names_monero_wallets[i])
        self.assertEqual(True, True)  # add assertion here
    def test_setData_Uphold(self):
        for i in np.arange(self.data_sources_dict["num_uphold_cards"]):
            self.dataGrabber.setData_Uphold(
                self.data_sources_dict["uphold_token"],
                self.data_sources_dict["uphold_cards"][i],i,1,False)
        for i in np.arange(self.data_sources_dict["num_uphold_cards"]):
            print(self.dataGrabber.balance_uphold_cards[i])
            print(self.dataGrabber.names_uphold_cards[i])
        self.assertEqual(True, True)  # add assertion here
    def test_setData_Coinbase(self):
        self.dataGrabber.setData_Coinbase(
            self.data_sources_dict["coinbase_api_key"],
            self.data_sources_dict["coinbase_api_secret"],1,False)
        for i in np.arange(self.data_sources_dict["num_coinbase_currencies"]):
            print(self.dataGrabber.balance_coinbase_currencies[i])
            print(self.dataGrabber.names_coinbase_currencies[i])
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
