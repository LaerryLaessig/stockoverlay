# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# LaerryLaessig wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return LaerryLaessig
# ----------------------------------------------------------------------------
from collections import namedtuple
from time import sleep

import requests
from colorama import init, Fore, Style

stocks = ('AMC', 'GRWG')

# raw data
StockData = namedtuple('StockData', 'name currency price change change_prct \
                                     pre_price pre_change pre_change_prct \
                                     post_price post_change post_change_prct')
# raw data formatted for printing
FormattedStockData = namedtuple('FormattedStockData', 'name price change change_prct \
                                                       pre_price pre_change pre_change_prct \
                                                       post_price post_change post_change_prct')


def currency_as_str(currency):
    if currency == 'USD':
        return '$'
    if currency == 'EUR':
        return '€'
    raise RuntimeError('Found unsupported currency: {}'.format(currency))


def format_stock_data(data: [StockData]):
    fmt_price = lambda x, y: '{:+.2f}{}'.format(x, y)
    fmt_change = lambda x: '{:+.2f}'.format(x)
    fmt_prct = lambda x: '{:+.2f}%'.format(x)
    return (FormattedStockData(
        name=d.name,
        price=fmt_price(d.price, currency_as_str(d.currency)),
        change=fmt_change(d.change),
        change_prct=fmt_prct(d.change_prct),
        pre_price=fmt_price(d.pre_price, currency_as_str(d.currency)) if d.pre_price else '',
        pre_change=fmt_change(d.pre_change) if d.pre_change else '',
        pre_change_prct=fmt_prct(d.pre_change_prct) if d.pre_change_prct else '',
        post_price=fmt_price(d.post_price, currency_as_str(d.currency)) if d.post_price else '',
        post_change=fmt_change(d.post_change) if d.post_change else '',
        post_change_prct=fmt_prct(d.post_change_prct) if d.post_change_prct else '',
    ) for d in data)


def get_yahoo_stock_data(stonks: [str]):
    base_url = 'https://query2.finance.yahoo.com/v7/finance/quote'
    symbols = ','.join(stonks)
    fields = ','.join(('currency',
                       'preMarketPrice', 'preMarketChange', 'preMarketChangePercent',
                       'regularMarketPrice', 'regularMarketChange', 'regularMarketChangePercent',
                       'postMarketPrice', 'postMarketChange', 'postMarketChangePercent'))
    query = '{}?symbols={}&fields={}'.format(base_url, symbols, fields)

    response = requests.get(query, headers={'User-agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        raise RuntimeError("Failed to parse Yahoo's response:\n{}", response.text)

    parsed = response.json()
    assert parsed['quoteResponse']
    assert parsed['quoteResponse']['result']

    return (StockData(
        name=r.get('symbol'),
        currency=r.get('currency'),
        price=r.get('regularMarketPrice'),
        change=r.get('regularMarketChange'),
        change_prct=r.get('regularMarketChangePercent'),
        pre_price=r.get('preMarketPrice', ''),
        pre_change=r.get('preMarketChange', ''),
        pre_change_prct=r.get('preMarketChangePercent', ''),
        post_price=r.get('postMarketPrice', ''),
        post_change=r.get('postMarketChange', ''),
        post_change_prct=r.get('postMarketChangePercent', '')
    ) for r in parsed['quoteResponse']['result'])


def change_color(change):
    return Fore.GREEN if '+' in change else Fore.RED if '-' in change else ''


def start():
    pre_name = '- pre'
    post_name = '- post'
    while True:
        to_print = []
        for data in format_stock_data(get_yahoo_stock_data(stocks)):
            to_print.append((data.name, data.price, data.change, data.change_prct))

            if data.pre_price:
                to_print.append((pre_name, data.pre_price, data.pre_change, data.pre_change_prct))

            if data.post_price:
                to_print.append((post_name, data.post_price, data.post_change, data.post_change_prct))

        name_width = max([len(d[0]) for d in to_print])
        price_width = max([len(d[1]) for d in to_print])
        change_width = max([len(d[2]) for d in to_print])
        change_prct_width = max([len(d[3]) for d in to_print])
        delimiter_width = 0

        for mode in ('measure', 'print'):
            for name, price, change, change_prct in to_print:
                out = '{name}: {price} {color_change}{change} {change_prct}{reset}'.format(
                    name=name.ljust(name_width),
                    price=price.rjust(price_width),
                    color_change=change_color(change) if mode == 'print' else '',
                    change=change.rjust(change_width),
                    change_prct=change_prct.rjust(change_prct_width),
                    reset=Style.RESET_ALL if mode == 'print' else '')
                if mode == 'print':
                    print(out)
                else:
                    delimiter_width = max(delimiter_width, len(out))

        print('=' * delimiter_width)
        # public api is limited by 2000 requests per hour
        sleep(3600 // 2000 + 1)


if __name__ == '__main__':
    init()
    start()
