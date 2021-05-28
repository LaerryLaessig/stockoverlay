from time import sleep
import requests
from colorama import init, Fore, Style
from collections import namedtuple
from bs4 import BeautifulSoup

StockData = namedtuple('Stock', 'name price change pre_price pre_change')

stocks = ['AMC', 'GRWG']

url = 'https://finance.yahoo.com/quote'
ele_id = 'quote-header-info'


def get_stock_data(stock: str):
    responce = requests.request('GET', url='{}/{}'.format(url, stock))
    soup = BeautifulSoup(responce.content, "html.parser")
    return StockData(name=stock,
                     price=soup.find(id=ele_id).find_all(attrs={"data-reactid": '32'})[0].text,
                     change=soup.find(id=ele_id).find_all(attrs={"data-reactid": '33'})[0].text,
                     pre_price=pre_prices[0].text if (pre_prices := soup.find(id=ele_id).find_all(attrs={"data-reactid": '38'})) else None,
                     pre_change=pre_changes[0].text if (pre_changes := soup.find(id=ele_id).find_all(attrs={"data-reactid": '40'})) else None)


def change_color(change):
    return Fore.GREEN if '+' in change else Fore.RED


def start():
    pre_name = '- pre'
    while True:
        loaded_data = [get_stock_data(stock) for stock in stocks]
        name_width = max([len(stock) for stock in stocks])
        price_width = max([len(data.price) for data in loaded_data])
        delimiter_width = 0

        for mode in ('measure', 'print'):
            for data in loaded_data:
                values = [(data.name, data.price, data.change)]

                if data.pre_price:
                    values.append((pre_name, data.pre_price, data.pre_change))
                    name_width = max(len(pre_name), name_width)

                for name, price, change in values:
                    out = '{name}: {price} $ {color_change}{change}{reset}'.format(
                            name=name.ljust(name_width),
                            price=price.rjust(price_width),
                            color_change=change_color(change) if mode == 'print' else '',
                            change=change,
                            reset=Style.RESET_ALL if mode == 'print' else '')
                    if mode == 'print':
                        print(out)
                    else:
                        delimiter_width = max(delimiter_width, len(out))

        print('=' * delimiter_width)
        sleep(30)


if __name__ == '__main__':
    init()
    start()
