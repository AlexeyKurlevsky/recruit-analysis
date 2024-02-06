import asyncio
import json
import logging

from functools import cached_property
from huntflow_api_client import HuntflowAPI
from huntflow_api_client.tokens import ApiToken

from src.config import HUNTFLOW_ACCESS_TOKEN, HUNTFLOW_REFRESH_TOKEN


class HuntHandler:
    def __init__(self, url: str = "https://api.huntflow.ru"):
        self.__token = ApiToken(access_token=HUNTFLOW_ACCESS_TOKEN,
                                refresh_token=HUNTFLOW_REFRESH_TOKEN)
        self.client = HuntflowAPI(base_url=url, token=self.__token,
                                  auto_refresh_tokens=True)
        self._current_user_id = self.current_user_id
        self._org_id = self.org_id
        self._total_vacancy = self.total_vacancy
        self._additional_fields = self.additional_fields

    @cached_property
    def current_user_id(self):
        resp = asyncio.run(self.client.request(method='GET', path='me'))
        if resp.status_code != 200:
            logging.info(resp.text)
            raise ValueError('Status code from getMe request %s' % resp.status_code)
        logging.info('Status code from getMe request %s' % resp.status_code)
        res = json.loads(resp.text)
        self._current_user_id = res.get('id')
        return self._current_user_id

    @cached_property
    def org_id(self):
        resp = asyncio.run(self.client.request(method='GET', path='accounts'))
        if resp.status_code != 200:
            logging.info(resp.text)
            raise ValueError('Status code from accounts request %s' % resp.status_code)
        logging.info('Status code from accounts request %s' % resp.status_code)
        res = json.loads(resp.text)
        if not res.get('items') and not res['items']:
            raise ValueError('Response don\'t have items key')
        self._org_id = res['items'][0]['id']
        return self._org_id

    @property
    def total_vacancy(self):
        path = f'accounts/{self._org_id}/vacancies'
        resp = asyncio.run(self.client.request(method='GET', path=path))
        if resp.status_code != 200:
            logging.info(resp.text)
            raise ValueError('Status code from get all vacancies request %s' % resp.status_code)
        logging.info('Status code from get all vacancies request %s' % resp.status_code)
        res = json.loads(resp.text)
        self._total_vacancy = res['total_items']
        return self._total_vacancy

    @cached_property
    def additional_fields(self):
        path = f'accounts/{self._org_id}/vacancies/additional_fields'
        resp = asyncio.run(self.client.request(method='GET', path=path))
        if resp.status_code != 200:
            logging.info(resp.text)
            raise ValueError('Status code from get additional fields request %s' % resp.status_code)
        res = json.loads(resp.text)
        self._additional_fields = list(res.keys())
        return self._additional_fields

    @property
    def request(self):
        return self.client.request



