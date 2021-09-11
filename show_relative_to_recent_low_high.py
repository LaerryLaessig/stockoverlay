# -----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# vmc <vmc.coding@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.
# -----------------------------------------------------------------------------

import argparse
import datetime
import sys
from collections import namedtuple
from time import sleep

import requests

Config = namedtuple('Config', ['symbols', 'width', 'historical_days', 'interval'])


def generate_bar(low, high, current, width=40):
    tokens = ['*' if current <= low else '|']

    if current == low or current == high:
        tokens.append('-' * (width - 2))
    else:
        current_range = max(current, high) - min(current, low)
        diff_current = abs(current - low) if current <= high else current - high
        prct_left = diff_current / current_range
        if current >= high:
            prct_left = 1 - prct_left
        filler_left = int((width - 1.5) * prct_left)
        filler_right = width - filler_left - 3
        tokens.append('-' * filler_left)
        tokens.append('*' if low < current < high else '|')
        tokens.append('-' * filler_right)

    tokens.append('*' if current >= high else '|')

    return ''.join(tokens)


def yahoo_query(query):
    response = requests.get(query, headers={'User-agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        raise RuntimeError("Failed to parse Yahoo's response:\n{}", response.text)
    return response


def yahoo_query_historical_lows_highs(start, end, symbols):
    result = {}
    url_template = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}' \
                   '&interval=1d&events=history'
    for symbol in symbols:
        response = yahoo_query(url_template.format(symbol, start.strftime('%s'), end.strftime('%s')))
        rows = [line.split(',') for line in response.text.splitlines()]
        headers = rows.pop(0)
        low_idx, high_idx = headers.index('Low'), headers.index('High')

        result[symbol] = {
            'low': min(float(row[low_idx]) for row in rows),
            'high': max(float(row[high_idx]) for row in rows)
        }
    return result


def yahoo_query_quotes(symbols):
    url_template = 'https://query2.finance.yahoo.com/v7/finance/quote?symbols={}&fields={}'
    fields = ','.join(('preMarketPrice', 'regularMarketPrice', 'postMarketPrice'))
    response = yahoo_query(url_template.format(','.join(symbols), fields))

    return ((result['symbol'],
             result.get('preMarketPrice') or result.get('postMarketPrice') or result.get('regularMarketPrice'))
            for result in response.json()['quoteResponse']['result'])


def main_loop(config: Config):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=config.historical_days)
    lows_highs = yahoo_query_historical_lows_highs(start, end, config.symbols)
    max_symbol_len = max(len(s) for s in config.symbols)
    bar_width = config.width - max_symbol_len - 1

    if bar_width < 5:
        raise RuntimeError('The width setting is too small, see parameter --width.')

    while True:
        for (symbol, value) in yahoo_query_quotes(config.symbols):
            print(symbol.rjust(max_symbol_len), end=' ')
            print(generate_bar(lows_highs[symbol]['low'], lows_highs[symbol]['high'], value, bar_width))
        sleep(config.interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Show the current value of financial securities in respect to recent low/highs',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('symbols', metavar='SYMBOL', nargs='+',
                        help='A symbol to query quotes for')
    parser.add_argument('--width', dest='width', type=int, default=40,
                        help='The width of the output string')
    parser.add_argument('--historical-days', dest='historical_days', type=int, default=7,
                        help='The number of days to look back to determine the recent low/high values')
    parser.add_argument('--interval', dest='interval', type=int, default=10,
                        help='The interval for quote polling in seconds')
    args = parser.parse_args()
    config = Config(
        symbols=args.symbols,
        width=args.width,
        historical_days=args.historical_days,
        interval=args.interval
    )

    try:
        main_loop(config)
    except RuntimeError as e:
        print('Error: {}'.format(e), file=sys.stderr)
