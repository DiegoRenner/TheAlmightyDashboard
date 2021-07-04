import unittest
from init_data_sources import DataSourceInitializer


class MyTestCase(unittest.TestCase):
    dataSourceInitializer = DataSourceInitializer("config.json")
    def test_get_num_uphold_cards(self):
        print(self.dataSourceInitializer.uphold_cards)
        self.assertEqual(True, True)  # add assertion here
    def test_get_num_coinbase_currencies(self):
        #self.dataSourceInitializer.set_num_coinbase_currencies()
        print(self.dataSourceInitializer.coinbase_currencies)
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
