import csv
import json
import os
import time
from datetime import date

import psutil as psutil
from loguru import logger
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.webdriver import WebDriver

PROCESS_NAME = ['chromedriver.exe', 'chrome.exe']
TODAY = str(date.today())
SCRL_XPTH = '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]'
SCRL_TIME = 2
logger.add(
    f'{os.getcwd()}\\logs\\logs.log - {TODAY}',
    format=' {level} | {time:MM-DD-YY | HH:mm:ss | dddd} | {message} ',
    level='DEBUG',
    rotation='1 day',
    compression='zip',
    # serialize=True
)


def create_driver() -> WebDriver:
    useragent = UserAgent()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--lang=en")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('ignore-certificate-errors')
    chrome_options.add_argument(f"user-agent={useragent.random}")
    chrome_options.add_argument("--disable-site-isolation-trials")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def timed(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = "[{name}]: Time spend: {elapsed:.2f}s".format(
            name=func.__name__.upper(),
            elapsed=time.time() - start
        )
        logger.success(duration)
        return result

    return wrapper


def kill_by_process() -> None:
    try:
        for proc in psutil.process_iter():
            for process_name in PROCESS_NAME:
                if proc.name() == process_name:
                    proc.kill()
    except Exception as ex:
        logger.warning(f"Session isn't closed [{str(ex)}]")
        os.system("taskkill /f /im " + PROCESS_NAME[0])
        logger.info('[KILL BY PROCESS SHELL]')


def open_txt(name_file: str) -> list:
    with open(name_file, "r", encoding='UTF-8') as file:
        return [line.replace("\n", "") for line in file]


def save_json(data: dict) -> None:
    with open(f'db\\companies_db - {TODAY}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=3)
    return logger.success(f'[SAVE JSON]')


def save_scv(data: dict) -> None:
    with open(f'db\\companies_db - {TODAY}.csv', 'w', newline='', encoding='UTF-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ('Google Place ID', 'Name', 'Address', 'City', 'State', 'State code', 'Country', 'Type', 'Status', 'URL')
        )
        for place_id, values in data.items():
            name = values.get('name', "")
            address = values.get('address', "")
            city = values.get('city', "")
            state = values.get('state', "")
            state_code = values.get('zip_code', "")
            country = values.get('country', "")
            company_type = values.get('type', "")
            status = values.get('business_status', "")
            url = values.get('gmb_url', "")
            writer.writerow((place_id, name, address, city, state, state_code, country, company_type, status, url))
    return logger.success(f'[SAVE SCV]')


def create_requests() -> list:
    return [f'https://www.google.com/maps/search/{rq} {st} US?hl=en' for st in open_txt("query_setup/locations.txt")
            for rq in open_txt("query_setup/requests.txt")]
