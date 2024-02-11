import asyncio
import logging
import json
import math

from typing import Any

from src.config import MAX_ITEM_ON_PAGE
# 2135 - закрыли сами
# 2136 - закрыла сторонняя компания


def async_request(client: Any, path: str, method: str = "GET", **kwargs):
    resp = asyncio.run(client.request(path=path, method=method, **kwargs))
    res = json.loads(resp.text)
    return res, resp.status_code


def remove_additional_column(elem, columns):
    for col in columns:
        try:
            del elem[col]
        except Exception as ex:
            logging.debug('additional column %s is missing' % col)
            continue
    return elem
