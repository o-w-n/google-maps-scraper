from loguru import logger


def clear_place_id(string: str) -> str:
    return string.replace('"', '').replace(']]]', '').replace('\\', '')


def get_place_id(response: str, url: str) -> [str, None]:
    try:
        for item in str(response).split(','):
            lower_item = item.lower()
            if "chij" in lower_item and len(item) < 36:
                place_id = clear_place_id(item)
                # place_id = place_id.split(place_id[:1]).pop(1)
                return place_id
        else:
            return None
    except Exception as ex:
        logger.error(f'[ERROR]: {url} | {str(ex)}')
