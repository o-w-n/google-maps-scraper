import time
import multiprocessing
from multiprocessing import Pool

from bs4 import BeautifulSoup
from loguru import logger
from selenium.webdriver.common.by import By
from companies_data import get_companies_dict
from config import SCRL_XPTH, SCRL_TIME, create_driver, create_requests, save_scv, kill_by_process, save_json, timed

driver = create_driver()


def scroll(scrolling_element_xpath: str) -> None:
    scrolling_element = driver.find_element(By.XPATH, scrolling_element_xpath)
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrolling_element)
    counter = 0
    while True:
        counter += 1
        driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', scrolling_element)
        time.sleep(SCRL_TIME)
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrolling_element)
        if new_height == last_height:
            break
        last_height = new_height
    if counter < 3:
        logger.warning(f'[SCROLLING]: {counter}')


def get_companies_urls() -> list:
    companies_urls = []
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    for values in soup.find_all('a'):
        company_url = values.get('href', None)
        if isinstance(company_url, str) and "www.google.com/maps/place" in company_url:
            companies_urls.append(company_url)
    return companies_urls


def scraping_google_maps(url: str) -> dict:
    try:
        driver.get(url)
        time.sleep(SCRL_TIME)
        scroll(SCRL_XPTH)
        iter_req_dict = get_companies_dict(get_companies_urls())
        return iter_req_dict
    except Exception as ex:
        logger.error(f'[ERROR]: {str(ex)} |')
        pass


@timed
def main() -> dict:
    main_dict = {}
    url_list = create_requests()
    counter = 0
    with Pool(processes=multiprocessing.cpu_count()) as pool:
        for company_dict in pool.imap_unordered(scraping_google_maps, url_list):
            try:
                counter += 1
                logger.info(f'[MAIN]: Progress: {counter}/{len(url_list)}')
                main_dict.update(company_dict)
            except Exception as ex:
                logger.error(f'[ERROR]: {str(ex)} |')
                pass
    kill_by_process()
    return main_dict


if __name__ == '__main__':
    main_data = main()
    save_scv(main_data)
    save_json(main_data)
