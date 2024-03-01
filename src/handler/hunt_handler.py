import asyncio
import json
import logging
import math

from sqlalchemy import insert
from datetime import datetime
from functools import cached_property
from huntflow_api_client import HuntflowAPI
from huntflow_api_client.tokens import ApiToken

from src.config import (
    HUNTFLOW_ACCESS_TOKEN,
    HUNTFLOW_REFRESH_TOKEN,
    engine,
    MAX_ITEM_ON_PAGE,
)
from src.db.tables import Coworkers, StatusReasons
from src.handler.func import async_request
from src.handler.hunt_token_proxy import HuntTokenProxy


class HuntHandler:
    def __init__(
        self,
        url: str = "https://api.huntflow.ru",
        access_token: str = HUNTFLOW_ACCESS_TOKEN,
    ):
        self.__token = ApiToken(
            access_token=access_token, refresh_token=HUNTFLOW_REFRESH_TOKEN
        )
        self.__token_proxy = HuntTokenProxy(token=self.__token)
        self.client = HuntflowAPI(
            base_url=url, token_proxy=self.__token_proxy, auto_refresh_tokens=True
        )
        self._current_user_id = self.current_user_id
        self._org_id, self._org_nick = self.org_id
        self._total_vacancy = self.total_vacancy
        self._additional_fields = self.additional_fields
        self._total_coworkers = self.total_coworkers

    @cached_property
    def current_user_id(self):
        resp = asyncio.run(self.client.request(method="GET", path="me"))
        if resp.status_code != 200:
            logging.error(resp.text)
            raise ValueError("Status code from getMe request %s" % resp.status_code)
        logging.info("Status code from getMe request %s" % resp.status_code)
        res = json.loads(resp.text)
        self._current_user_id = res.get("id")
        return self._current_user_id

    @cached_property
    def org_id(self):
        resp = asyncio.run(self.client.request(method="GET", path="accounts"))
        if resp.status_code != 200:
            logging.error(resp.text)
            raise ValueError("Status code from accounts request %s" % resp.status_code)
        logging.info("Status code from accounts request %s" % resp.status_code)
        res = json.loads(resp.text)
        if not res.get("items") and not res["items"]:
            raise ValueError("Response don't have items key")
        self._org_id = res["items"][0]["id"]
        self._org_nick = res["items"][0]["nick"]
        return self._org_id, self._org_nick

    @property
    def total_vacancy(self):
        path = f"accounts/{self._org_id}/vacancies"
        resp = asyncio.run(self.client.request(method="GET", path=path))
        if resp.status_code != 200:
            logging.error(resp.text)
            raise ValueError(
                "Status code from get all vacancies request %s" % resp.status_code
            )
        logging.info("Status code from get all vacancies request %s" % resp.status_code)
        res = json.loads(resp.text)
        self._total_vacancy = res["total_items"]
        return self._total_vacancy

    @cached_property
    def additional_fields(self):
        path = f"accounts/{self._org_id}/vacancies/additional_fields"
        resp = asyncio.run(self.client.request(method="GET", path=path))
        if resp.status_code != 200:
            logging.error(resp.text)
            raise ValueError(
                "Status code from get additional fields request %s" % resp.status_code
            )
        res = json.loads(resp.text)
        self._additional_fields = list(res.keys())
        return self._additional_fields

    @cached_property
    def total_coworkers(self):
        path = f"accounts/{self._org_id}/coworkers"
        resp = asyncio.run(self.client.request(method="GET", path=path))
        if resp.status_code != 200:
            logging.error(resp.text)
            raise ValueError(
                "Status code from get all coworkers request %s" % resp.status_code
            )
        res = json.loads(resp.text)
        self._total_coworkers = res["total_items"]
        return self._total_coworkers

    @property
    def request(self):
        return self.client.request

    def update_coworkers(self, coworker_info: dict):
        path = f'accounts/{self._org_id}/users/{coworker_info["id"]}'
        try:
            resp = asyncio.run(self.client.request(method="GET", path=path))
            res = json.loads(resp.text)
        except Exception as ex:
            logging.error(ex.errors[0].title)
            res = {
                "id": coworker_info["id"],
                "name": coworker_info["name"],
                "type": "unknown",
            }
        try:
            stmt = insert(Coworkers).values(
                id=res["id"], name=res["name"], type=res["type"]
            )
            with engine.connect() as conn:
                result = conn.execute(stmt)
        except Exception as ex:
            logging.error(ex)

    def update_status_reasons(self, status_id: tuple):
        path_dict = {
            "hold": f"/accounts/{self._org_id}/vacancy_hold_reasons",
            "close": f"/accounts/{self._org_id}/vacancy_close_reasons",
        }
        path = path_dict[status_id[0]]

        resp = asyncio.run(self.client.request(method="GET", path=path))
        logging.debug("Status code get reasons %s" % resp.status_code)
        if resp.status_code != 200:
            logging.error(resp.text)
            raise ValueError("Status code from get status %s" % resp.status_code)
        res = json.loads(resp.text)
        getting_status = {elem["id"]: elem["name"] for elem in res["items"]}
        name = getting_status[status_id[1]]
        try:
            stmt = insert(StatusReasons).values(id=status_id[1], name=name)
            with engine.connect() as conn:
                result = conn.execute(stmt)
        except Exception as ex:
            logging.error(ex)

    def get_all_vacancies(self):
        path = f"accounts/{self._org_id}/vacancies"
        count_page = math.ceil(self._total_vacancy / MAX_ITEM_ON_PAGE)
        arr_vac = []
        for i in range(1, count_page + 1):
            data = {"count": MAX_ITEM_ON_PAGE, "page": i}
            resp, status = async_request(self.client, path=path, params=data)
            if status != 200:
                raise ValueError("Can't getting all vacancies")
            arr_vac += resp["items"]
        return arr_vac

    def get_log_vacancy(self, vacancy_id, date_begin):
        path = f"/accounts/{self._org_id}/vacancies/{vacancy_id}/logs"
        date_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+03:00")
        params = {"date_begin": date_begin, "date_end": date_now}

        resp = asyncio.run(self.client.request(method="GET", path=path, params=params))
        logging.debug("response code from log vacancy %s" % resp.status_code)

        if resp.status_code != 200:
            logging.error(resp.text)
            return None
        res = json.loads(resp.text)

        if res["items"]:
            log = res["items"][0]
        else:
            log = None

        return log

    def check_reason_close(self, vacancy_id):
        path = f"/accounts/{self._org_id}/vacancies/{vacancy_id}/frame"
        flg = False
        try:
            resp = asyncio.run(self.client.request(method="GET", path=path))
            res = json.loads(resp.text)
            if res["hired_applicants"]:
                flg = True
        except Exception as ex:
            logging.error(ex)

        return flg
