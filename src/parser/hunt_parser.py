import logging
from functools import cached_property

from bs4 import BeautifulSoup
from requests import Session

from src.config import HUNTFLOW_ACCESS_TOKEN, HUNTFLOW_PASSWORD, HUNTFLOW_URL, HUNTFLOW_URL_API, HUNTFLOW_USERNAME
from src.handler.hunt_handler import HuntHandler
from src.parser.func import get_info_vacancy


logger = logging.getLogger()


class HuntFlowParser:
    def __init__(self, url_parse: str = HUNTFLOW_URL, url_api: str = HUNTFLOW_URL_API):
        self.url_parse = url_parse
        self.url_api = url_api
        self.session = Session()
        self._org_nick = self.get_org_nick
        self.login_flg = False

    def login(self) -> None:
        login_url = f"{self.url_parse}/account/login"
        login_page = self.session.get(login_url)
        soup = BeautifulSoup(login_page.content, "html.parser")
        csrf_token_data = soup.find("meta", {"name": "xsrf"})
        if not csrf_token_data or not csrf_token_data.get("content"):
            logger.error("Не смог получить csrf токен")
            raise ValueError("Не смог получить csrf токен")
        csrf_token = csrf_token_data.get("content")
        payload = {"email": HUNTFLOW_USERNAME, "password": HUNTFLOW_PASSWORD, "_xsrf": csrf_token}

        login_response = self.session.post(login_url, data=payload)

        if not login_response.ok:
            logger.error("Login failed!!!")
            logger.error(login_response.text)
            raise ValueError("Login failed")

        logger.info("Login successful!!!!")

        self.login_flg = True

    @cached_property
    def get_org_nick(self) -> str:
        handler = HuntHandler(self.url_api, access_token=HUNTFLOW_ACCESS_TOKEN)
        self._org_nick = handler.org_id[1]
        return self._org_nick

    def get_vacancy_stat_info(self, vac_id: int) -> dict[str, tuple[str, int]] | None:
        if not self.login_flg:
            self.login()
        url_status = f"{self.url_parse}/my/{self._org_nick}/vacancy/{vac_id}/notify"
        logger.info(f"Отправляю запрос на получение статусов по вакансии {vac_id} по адресу {url_status}")
        notify_status = self.session.get(url_status)
        if not notify_status.ok:
            logger.error(f"Не удалось получить статусы по вакансии {vac_id}")
            return None
        logger.info(f"Получили статусы по вакансии {vac_id}")
        notify_data = notify_status.json()
        status_serialize = {}
        for status in notify_data["items"]:
            status_serialize[str(status["id"])] = status["name"]

        statistic_url = f"{self.url_parse}/my/{self._org_nick}/vacancy/{vac_id}/stats"
        logger.info(f"Отправляю запрос на получение статистики {statistic_url}")
        statistic_resp = self.session.get(statistic_url)
        if not statistic_resp.ok:
            logger.error(f"Не удалось получить статистику по вакансии {vac_id}")
            return None

        ans = {}
        statistics = statistic_resp.json()
        for status_id, value in statistics["items"].items():
            # может понадобится
            if status_id == "total":
                continue
            status_name = status_serialize.get(status_id)
            if status_name is None:
                logger.error(f"Не нашел информации по статусу {status_id}")
                continue
            ans[status_id] = (status_serialize[status_id], value)

        return ans

    def logout(self) -> None:
        url = f"{self.url_parse}/account/logout"
        resp = self.session.get(url)
        if resp.status_code == 200:
            logger.info("Logout!!!")
