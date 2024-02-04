import logging
import json

from huntflow_api_client import HuntflowAPI
from huntflow_api_client.tokens import ApiToken

from src.config import HUNTFLOW_ACCESS_TOKEN, HUNTFLOW_REFRESH_TOKEN

hunt_token = ApiToken(access_token=HUNTFLOW_ACCESS_TOKEN,
                      refresh_token=HUNTFLOW_REFRESH_TOKEN)
hunt_client = HuntflowAPI(base_url='https://api.huntflow.ru',
                          token=hunt_token,
                          auto_refresh_tokens=True)


async def get_me():
    resp = await hunt_client.request(method='GET', path='me')
    if resp.status_code != 200:
        logging.info('Status code from getMe request %s' % resp.status_code)
        raise ValueError(resp.text)
    logging.info('Status code from getMe request %s' % resp.status_code)
    res = json.loads(resp.text)
    return res
