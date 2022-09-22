import asyncio
import platform

import aiohttp
from loguru import logger
from bs4 import BeautifulSoup
from aiohttp import ClientSession

from place_id import get_place_id
from business_status import get_status

companies_by_location = {}


def get_company_type(response: str, url: str) -> str:
    try:
        soup = BeautifulSoup(response, 'html.parser')
        company_type = soup.find("meta", property="og:description")
        company_type = (company_type["content"] if company_type else "No meta title")
        return company_type.split("·").pop(1).strip() if "·" in company_type else company_type.strip()
    except Exception as ex:
        logger.error(f'ERROR]: {str(ex)} | {url} |')
        pass


def get_company_data(response: str, url: str) -> dict:
    try:
        soup = BeautifulSoup(response, 'html.parser')
        title = soup.find("meta", property="og:title")
        title = (title["content"] if title else "No meta title")
        if '·' in title and title.count(',') >= 3:
            title = title.split('·')
            if 'United States' in title[1]:
                return {
                    'name': title[0].strip(),
                    'address': title[1].split(',')[-4].strip(),
                    'city': title[1].split(',')[-3].strip(),
                    'state': title[1].split(',')[-2].split()[0].strip(),
                    'zip_code': title[1].split(',')[-2].split()[1].strip(),
                    'country': title[1].split(',')[-1].strip(),
                    'type': get_company_type(response, url),
                    'business_status': get_status(response, url)
                }
            else:
                return {
                    'name': title[0],
                    'address': None,
                    'city': None,
                    'state': None,
                    'zip_code': None,
                    'country': title[1].split(',')[-1].strip(),
                    'type': None,
                    'business_status': None
                }
        else:
            return {
                'name': title,
                'address': None,
                'city': None,
                'state': None,
                'zip_code': None,
                'country': None,
                'type': get_company_type(response, url),
                'business_status': get_status(response, url)
            }
    except (IndexError, TypeError) as ex:
        logger.error(f'[ERROR]: {str(ex)} | {url} |')
        pass


async def get_responses(session: ClientSession, url: str) -> None:
    company_dict = {}
    try:
        async with session.get(url) as response:
            assert response.status == 200
            response_text = await response.text()
            place_id = get_place_id(response_text, url)
            company_dict.update({place_id: {}})
            company_data = get_company_data(response_text, url)
            company_dict[place_id] = {
                'name': company_data.get('name', ''),
                'address': company_data.get('address', ''),
                'city': company_data.get('city', ''),
                'state': company_data.get('state', ''),
                'zip_code': company_data.get('zip_code', ''),
                'country': company_data.get('country', ''),
                'type': company_data.get('type', ''),
                'business_status': company_data.get('business_status', ''),
                'gmb_url': url,
            }
            companies_by_location.update(company_dict)
    except Exception as ex:
        logger.error(f'[ERROR]: {str(ex)} | {url} |')
        pass


async def create_tasks(urls_list: list) -> None:
    async with aiohttp.ClientSession(trust_env=True) as session:
        tasks = []
        for url in urls_list:
            task = asyncio.create_task(get_responses(session, url))
            tasks.append(task)
        await asyncio.gather(*tasks)


def get_companies_dict(urls_list: list) -> dict:
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(create_tasks(urls_list))
    return companies_by_location
