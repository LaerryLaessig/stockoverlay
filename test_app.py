import unittest

from app import currency_as_str, StockData, format_stock_data, FormattedStockData


class CurrencyAsStr(unittest.TestCase):
    def test_currency_dollar(self):
        self.assertEqual(currency_as_str('USD'), '$')

    def test_currency_unknown(self):
        with self.assertRaises(RuntimeError) as ctx:
            currency_as_str('DDR_MARK')
        self.assertTrue('Found unsupported currency: DDR_MARK' in str(ctx.exception))


class FormatStockData(unittest.TestCase):
    def test_max_data(self):
        data = [StockData(name='stock_name',
                          currency='USD',
                          price=1.2345,
                          change=0.34567,
                          change_prct=23.456789,
                          pre_price=-2.3456,
                          pre_change=-0.1234,
                          pre_change_prct=10.213545,
                          post_price=3.4567,
                          post_change=1.34567,
                          post_change_prct=8.987)]
        result = [FormattedStockData(name='stock_name',
                                     price='+1.23$',
                                     change='+0.35',
                                     change_prct='+23.46%',
                                     pre_price='-2.35$',
                                     pre_change='-0.12',
                                     pre_change_prct='+10.21%',
                                     post_price='+3.46$',
                                     post_change='+1.35',
                                     post_change_prct='+8.99%')]
        self.assertEqual(format_stock_data(data), result)

    def test_min_data(self):
        data = [StockData(name='stock_name',
                          currency='USD',
                          price=1.2345,
                          change=0.34567,
                          change_prct=23.456789,
                          pre_price=None,
                          pre_change=None,
                          pre_change_prct=None,
                          post_price=None,
                          post_change=None,
                          post_change_prct=None)]
        result = [FormattedStockData(name='stock_name',
                                     price='+1.23$',
                                     change='+0.35',
                                     change_prct='+23.46%',
                                     pre_price=None,
                                     pre_change=None,
                                     pre_change_prct=None,
                                     post_price=None,
                                     post_change=None,
                                     post_change_prct=None)]
        self.assertEqual(format_stock_data(data), result)


if __name__ == '__main__':
    unittest.main()
