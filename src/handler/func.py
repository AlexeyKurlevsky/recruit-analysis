import asyncio
import json
import logging
from typing import Any


logger = logging.getLogger()

# 2135 - закрыли сами
# 2136 - закрыла сторонняя компания


def async_request(client: Any, path: str, method: str = "GET", **kwargs):
    """
    Реализация запроса через клиента HF
    :param client: Сам клиент HF
    :param path: путь запроса
    :param method: метод запроса (GET, POST...)
    :param kwargs:
    :return:
    """
    resp = asyncio.run(client.request(path=path, method=method, **kwargs))
    res = json.loads(resp.text)
    return res, resp.status_code


def remove_additional_column(elem, columns):
    """
    Убирает ключ доп столбца у вакансии
    :param elem:
    :param columns:
    :return:
    """
    for col in columns:
        try:
            del elem[col]
        except Exception as ex:
            logger.error(ex)
            logger.debug(f"additional column {col} is missing")
            continue
    return elem
