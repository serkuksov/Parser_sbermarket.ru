import logging
import re
import time
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc


BROWSER_PATH = '/opt/google/chrome/chrome'


def get_token_from_chrom() -> str:
    """Получить токен открыв Сбермаркет в хроме.
    В случае если путь к браузеру не определился автоматически укажите его принудительно
    в переменной BROWSER_PATH"""
    driver_path = ChromeDriverManager().install()
    logging.info('Открываю браузер хром для получения токена')
    try:
        driver = uc.Chrome(driver_executable_path=driver_path)
    except TypeError:
        logging.error('Не найден путь к браузеру Chrome. Считываю путь из переменной BROWSER_PATH')
        try:
            driver = uc.Chrome(driver_executable_path=driver_path, browser_executable_path=BROWSER_PATH)
        except FileNotFoundError:
            logging.error(f'Не корректно задан путь к браузеру Chrome в переменной BROWSER_PATH={BROWSER_PATH}')
            raise FileNotFoundError
    driver.get('https://sbermarket.ru/')
    time.sleep(5)
    token = re.findall('STOREFRONT_API_V3_CLIENT_TOKEN: "([^"]+)"', driver.page_source)[0]
    driver.quit()
    logging.info(f'Токен получен: {token}')
    save_token_in_file(token=token)
    return token


def save_token_in_file(token: str):
    """Сохраняет токен в файл"""
    with open('token.txt', 'w', encoding='utf-8') as f:
        f.write(token)
    logging.info('Токен сохранен в файл')


def get_token_from_file() -> str:
    """Получить токен из файла"""
    try:
        with open('token.txt', 'r', encoding='utf-8') as f:
            token = f.read()
    except FileNotFoundError:
        logging.error('Файл с токеном не найден')
        token = get_token_from_chrom()
    return token
