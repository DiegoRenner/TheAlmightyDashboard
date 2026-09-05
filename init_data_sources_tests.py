import os
import unittest
from init_data_sources import DataSourceInitializer


class MyTestCase(unittest.TestCase):
    config_path = "config.json" if os.path.exists("config.json") else "config_no_accounts.json"
    dataSourceInitializer = DataSourceInitializer(config_path)
    def test_get_num_uphold_cards(self):
        print(self.dataSourceInitializer.uphold_cards)
        self.assertEqual(True, True)  # add assertion here
    def test_get_num_coinbase_currencies(self):
        #self.dataSourceInitializer.set_num_coinbase_currencies()
        print(self.dataSourceInitializer.coinbase_currencies)
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
