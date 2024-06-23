import logging
import os
from typing import Any, Dict

import dotenv
from airflow.models import Variable
from huntflow_api_client.tokens import ApiToken
from huntflow_api_client.tokens.proxy import DummyHuntflowTokenProxy, convert_refresh_result_to_hf_token


def set_env_in_file(key: str, value: str) -> None:
    """
    Обновить токены в переменных окружениях
    и переменных airflow
    :param key:
    :param value:
    :return:
    """
    os.environ[key] = value
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    dotenv.set_key(dotenv_file, key, os.environ[key])
    Variable.update(key=key, value=value)
    logging.info("Set new variable %s" % key)


class HuntTokenProxy(DummyHuntflowTokenProxy):
    def __init__(self, token: ApiToken):
        super().__init__(token)

    async def update(self, refresh_result: Dict[str, Any]) -> None:
        self._token = convert_refresh_result_to_hf_token(refresh_result, self._token)
        try:
            set_env_in_file("HUNTFLOW_ACCESS_TOKEN", self._token.access_token)
            logging.info("Rewrite new huntflow access token in .env file")
            set_env_in_file("HUNTFLOW_REFRESH_TOKEN", self._token.refresh_token)
            logging.info("Rewrite new huntflow refresh token in .env file")
        except Exception as ex:
            logging.error(ex)
