import os
import logging
import dotenv
from typing import Dict, Any

from huntflow_api_client.tokens import ApiToken
from huntflow_api_client.tokens.proxy import DummyHuntflowTokenProxy, convert_refresh_result_to_hf_token


def set_env_in_file(key: str) -> None:
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    dotenv.set_key(dotenv_file, key, os.environ[key])
    logging.info('Set new variable %s' % key)


class HuntTokenProxy(DummyHuntflowTokenProxy):
    def __init__(self, token: ApiToken):
        super().__init__(token)

    async def update(self, refresh_result: Dict[str, Any]) -> None:
        self._token = convert_refresh_result_to_hf_token(refresh_result, self._token)
        os.environ["HUNTFLOW_ACCESS_TOKEN"] = self._token.access_token
        set_env_in_file("HUNTFLOW_ACCESS_TOKEN")
        os.environ["HUNTFLOW_REFRESH_TOKEN"] = self._token.refresh_token
        set_env_in_file("HUNTFLOW_REFRESH_TOKEN")
