from time import sleep
import requests
from colorama import init, Fore
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


def start():
    while True:
        for stock in stocks:
            data = get_stock_data(stock)
            print('{color_main}{name}:\t{price} $\t{color_change}{change}'.format(
                color_main=Fore.WHITE,
                name=data.name,
                price=data.price,
                color_change=Fore.GREEN if '+' in data.change else Fore.RED,
                change=data.change))
            if data.pre_price is not None:
                print('{color_main}- pre\t{pre_price} $\t{color_change}{pre_change}'.format(
                    color_main=Fore.WHITE,
                    pre_price=data.pre_price,
                    color_change=Fore.GREEN if '+' in data.pre_change else Fore.RED,
                    pre_change=data.pre_change))
        sleep(30)
        print('{color_main}{break_char}'.format(
            color_main=Fore.WHITE,
            break_char='=' * 32))


if __name__ == '__main__':
    init()
    start()
