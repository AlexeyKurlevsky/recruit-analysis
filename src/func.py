import asyncio
import logging
import json
import math

from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import insert

from src.config import engine, MAX_VACANCIES_ON_PAGE
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


def insert_new_vacancies():
    handler = HuntHandler()
    rows = session.query(AllVacancies).count()
    diff = handler.total_vacancy - rows

    if diff <= 0:
        logging.info('all vacancies added')
        return None

    path = f'accounts/{handler.org_id}/vacancies'
    arr_vac = []
    if diff <= MAX_VACANCIES_ON_PAGE:
        data = {"count": diff}
        resp, status = async_request(handler.client, path=path, params=data)
        if status != 200:
            raise ValueError('Can\'t getting all vacancies')
        arr_vac += resp['items']
    else:
        count_page = math.ceil(diff / MAX_VACANCIES_ON_PAGE)
        for i in range(1, count_page+1):
            data = {"count": MAX_VACANCIES_ON_PAGE,
                    "page": i}
            resp, status = async_request(handler.client, path=path, params=data)
            if status != 200:
                raise ValueError('Can\'t getting all vacancies')

            # TODO: Добавить динамическое создание столбца
            resp['items'] = [remove_additional_column(elem, handler.additional_fields) for elem in resp['items']]
            arr_vac += resp['items']

        for row in arr_vac:
            stmt = insert(AllVacancies).values(**row)
            with engine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()

    logging.info(f'Get {len(arr_vac)} new vacancies')







