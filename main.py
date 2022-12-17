import logging
import time
from pprint import pprint
import requests
from silenium_parser import get_token_from_file, get_token_from_chrom


def get_products(name_products: str, number_market: int = 62) -> list[dict]:
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
        response = requests.get(f'https://sbermarket.ru/api/v3/stores/{number_market}/products',
                                params=params,
                                headers=headers)
        if 'errors' in response.text:
            headers['client-token'] = get_token_from_chrom()
            response = requests.get(f'https://sbermarket.ru/api/v3/stores/{number_market}/products',
                                    params=params,
                                    headers=headers)
        content_json = response.json()
        total_pages = int(content_json['meta']['total_pages'])
        total_count = int(content_json['meta']['total_count'])
        products += content_json['products']
        if page == total_pages:
            logging.info(f'Получено {total_count} из {total_count} продуктов')
            break
        logging.info(f'Получено {page * 20} из {total_count} продуктов')
        page += 1
        time.sleep(1)
    return products


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        products = get_products(name_products='сок', number_market=62)
        pprint(products)
    except FileNotFoundError:
        pass
