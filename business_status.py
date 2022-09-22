from bs4 import BeautifulSoup
from loguru import logger


def get_status(response: str, url: str) -> str:
    try:
        soup = BeautifulSoup(response, features="html.parser")
        for item in str(soup).split(','):
            lower_item = item.lower()
            status_list = ['Temporarily closed', 'Permanently closed', 'Operational']
            for status in status_list:
                if status.lower() in lower_item:
                    status = item.replace('"', '').replace(']]]', '')
                    status = status.split(status[:1]).pop(1)
                    if len(status) <= 20:
                        return status
    except Exception as ex:
        logger.error(f'[{url}]: NO STATUS | {str(ex)}')
    return 'Operational'
