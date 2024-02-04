from huntflow_api_client import HuntflowAPI
from huntflow_api_client.tokens import ApiToken

from config import HUNTFLOW_ACCESS_TOKEN, HUNTFLOW_REFRESH_TOKEN

hunt_token = ApiToken(access_token=HUNTFLOW_ACCESS_TOKEN, refresh_token=HUNTFLOW_REFRESH_TOKEN)
hunt_client = HuntflowAPI(token=hunt_token, auto_refresh_tokens=True)
