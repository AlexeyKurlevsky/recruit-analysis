import logging
import os
from typing import Any

import dotenv
from airflow.models import Variable
from huntflow_api_client.tokens import ApiToken
from huntflow_api_client.tokens.proxy import DummyHuntflowTokenProxy, convert_refresh_result_to_hf_token


logger = logging.getLogger()


def set_env_in_file(key: str, value: str | None) -> None:
    """
    Обновить токены в переменных окружениях
    и переменных airflow
    :param key:
    :param value:
    :return:
    """
    if value is None:
        logger.error(f"For {key} get None value")
        raise ValueError(f"For {key} get None value")
    os.environ[key] = value
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    dotenv.set_key(dotenv_file, key, os.environ[key])
    Variable.update(key=key, value=value)
    logger.info(f"Set new variable {key}")


class HuntTokenProxy(DummyHuntflowTokenProxy):
    def __init__(self, token: ApiToken):
        super().__init__(token)  # pylint

    async def update(self, refresh_result: dict[str, Any]) -> None:
        self._token = convert_refresh_result_to_hf_token(refresh_result, self._token)
        try:
            set_env_in_file("HUNTFLOW_ACCESS_TOKEN", self._token.access_token)
            logger.info("Rewrite new huntflow access token in .env file")
            set_env_in_file("HUNTFLOW_REFRESH_TOKEN", self._token.refresh_token)
            logger.info("Rewrite new huntflow refresh token in .env file")
        except Exception as ex:
            logger.error(ex)
