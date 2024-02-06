import asyncio
import logging
import json
import math

from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import insert

from src.config import engine, MAX_ITEM_ON_PAGE
from src.db.tables import AllVacancies
from src.handler import HuntHandler

session = Session(bind=engine)


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


def check_new_row(diff, handler, path):
    arr_vac = []
    if diff <= MAX_ITEM_ON_PAGE:
        data = {"count": diff}
        resp, status = async_request(handler.client, path=path, params=data)
        if status != 200:
            raise ValueError('Can\'t getting all vacancies')
        arr_vac += resp['items']
    else:
        count_page = math.ceil(diff / MAX_ITEM_ON_PAGE)
        for i in range(1, count_page+1):
            data = {"count": MAX_ITEM_ON_PAGE,
                    "page": i}
            resp, status = async_request(handler.client, path=path, params=data)
            if status != 200:
                raise ValueError('Can\'t getting all vacancies')
            arr_vac += resp['items']
    return arr_vac
