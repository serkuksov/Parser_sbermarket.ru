import logging
import time
from pprint import pprint
import requests
from silenium_parser import get_token_from_file, get_token_and_cookies_from_chrom, get_cookies_from_file


def get_products(name_products: str,
                 number_market: int,
                 delay: float = 0.2,
                 need_other_params: bool = True,
                 proxies: dict[str: str] = None) -> list[dict]:
    """Функция получения информации по продуктам из определенного магазина
    по наименованию.
    В качестве донора используется сайт https://sbermarket.ru/ на котором
    имеется информация по продуктам с различных магазинов.
    Для выбора конкретного магазина нужно передать его номер.
    Номер магазина можно узнать перейдя на его страницу на сайте https://sbermarket.ru/.

    Например магазин МЕТРО в Казани расположен по адресу https://sbermarket.ru/metro?sid=62,
    где параметр sid=62 отображает номер магазина требуемый для работы функции.
    """
    products = []
    page = 1
    number_products = 1
    logging.info('Начинаю получать информация по продуктам')
    while True:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru,en;q=0.9',
            'api-version': '3.0',
            'client-token': get_token_from_file(),
        }
        params = {
            'q': name_products,
            'page': page,
            'per_page': '20',
        }
        url = f'https://sbermarket.ru/api/v3/stores/{number_market}/products'
        response = requests.get(url=url, params=params, headers=headers, proxies=proxies)
        if response.status_code == 401:
            headers['client-token'] = get_token_and_cookies_from_chrom()['token']
            response = requests.get(url=url, params=params, headers=headers, proxies=proxies)
        content_json = response.json()
        total_pages = int(content_json['meta']['total_pages'])
        total_count = int(content_json['meta']['total_count'])
        for product in content_json['products']:
            params = {
                'id': product['id'],
                'name': product['name'],
                'image_urls': product['image_urls'],
                'price': product['price'],
                'original_price': product['original_price'],
                'number_products': number_products
            }
            if need_other_params:
                url_product = f'https://sbermarket.ru/api/stores/{number_market}/products/{product["slug"]}'
                other_params = get_other_params_product(url_product=url_product, proxies=proxies)
                params = {**params, **other_params}
            products.append(params)
            logging.info(f'Получено {number_products} из {total_count} продуктов')
            number_products += 1
        if page == total_pages:
            logging.info(f'Получено {total_count} из {total_count} продуктов')
            break
        page += 1
        time.sleep(delay)
    return products


def get_other_params_product(url_product: str, proxies: dict[str: str] = None) -> dict:
    """Функция получения дополнительных параметров для продуктов"""
    headers = {
        'referer': 'https://sbermarket.ru/metro/search?keywords=cjr',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/108.0.0.0 Safari/537.36'
    }
    cookies = get_cookies_from_file()
    response = requests.get(url=url_product, cookies=cookies, headers=headers, proxies=proxies)
    if response.status_code == 503:
        logging.error('Куки не актуальны')
        cookies = get_token_and_cookies_from_chrom()['cookies']
        response = requests.get(url=url_product, cookies=cookies, headers=headers, proxies=proxies)
    content_json = response.json()
    other_params = {
        'brand': content_json['product']['brand']['name'],
        'stock': content_json['product']['offer']['stock'],
        'category': content_json['product_taxons'][-1]['name'],
    }
    return other_params


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Пример для прокси
    # Селениум работает без прокси!!!! только реквест
    # proxies = {
    #     'http': 'http://85.26.146.169:80',
    #     'https': 'http://185.15.172.212:3128',
    # }
    proxies = None
    try:
        products = get_products(name_products='сок', number_market=62, proxies=proxies)
        pprint(products)
    except FileNotFoundError:
        pass
