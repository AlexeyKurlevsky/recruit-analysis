import logging
from functools import cached_property, wraps

from bs4 import BeautifulSoup
from requests import Session

from src.config import HUNTFLOW_ACCESS_TOKEN, HUNTFLOW_PASSWORD, HUNTFLOW_URL, HUNTFLOW_URL_API, HUNTFLOW_USERNAME
from src.handler.hunt_handler import HuntHandler
from src.parser.data_serialiaze import ApplicantStatistic, ApplicantValueByStatus, ApplucantStatusResponse
from src.parser.func import get_info_vacancy


STATUS_NAME_IN_WORK = "workon"
STATUS_NAME_RESPONSE = "response"

logger = logging.getLogger()


def login_required(func):
    wraps(func)

    def wrap(self, *args, **kwargs):
        if not self.login_flg:
            self.login()
        return func(self, *args, **kwargs)

    return wrap


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

    @login_required
    def get_applicant_status(self, vac_id: int) -> list[ApplucantStatusResponse]:
        url_status = f"{self.url_parse}/my/{self._org_nick}/vacancy/{vac_id}/notify"
        logger.info(f"Отправляю запрос на получение статусов по вакансии {vac_id} по адресу {url_status}")
        notify_status = self.session.get(url_status)
        if not notify_status.ok:
            text = f"Не удалось получить статусы по вакансии {vac_id}"
            logger.error(text)
            raise ValueError(text)
        logger.info(f"Получили статусы по вакансии {vac_id}")
        notify_data = notify_status.json()
        ans = [
            ApplucantStatusResponse(status_id=status["id"], status_name=status["name"])
            for status in notify_data["items"]
        ]
        return ans

    @login_required
    def get_common_applicant_status_value(self, vac_id: int) -> list[ApplicantStatistic]:
        statistic_url = f"{self.url_parse}/my/{self._org_nick}/vacancy/{vac_id}/stats"
        logger.info(f"Отправляю запрос на получение общей статистики {statistic_url}")
        statistic_resp = self.session.get(statistic_url)
        if not statistic_resp.ok:
            text = f"Не удалось получить статистику по вакансии {vac_id}"
            logger.error(text)
            raise ValueError(text)
        statistics = statistic_resp.json()
        ans = [
            ApplicantStatistic(status_id=int(status_id), value=value)
            for status_id, value in statistics["items"].items()
            if status_id != "total"
        ]
        return ans

    @login_required
    def get_current_applicant_status_value(self, vac_id: int) -> list[ApplicantStatistic]:
        url = f"{self.url_parse}/my/{self._org_nick}/applicants/status/stats?vacancy={vac_id}"
        logger.info(f"Отправляю запрос на текущей  общей статистики {url}")
        response = self.session.get(url)
        if not response.ok:
            text = f"Не удалось получить текущую статистику по вакансии {vac_id}"
            logger.error(text)
            raise ValueError(text)
        statistics = response.json()
        ans = [
            ApplicantStatistic(status_id=status["status"], value=status["current"])
            for status in statistics["items"]
            if status["status"] not in [STATUS_NAME_IN_WORK, STATUS_NAME_RESPONSE]
        ]
        return ans

    @login_required
    def get_vacancy_stat_info(self, vac_id: int) -> list[ApplicantValueByStatus]:
        statuses = self.get_applicant_status(vac_id)
        common_value_by_status = self.get_common_applicant_status_value(vac_id)
        current_value_by_status = self.get_current_applicant_status_value(vac_id)

        status_serialize = {status.status_id: status.status_name for status in statuses}
        common_value_serialize = {status.status_id: status.value for status in common_value_by_status}
        current_value_serialize = {status.status_id: status.value for status in current_value_by_status}

        ans = []
        for status, status_name in status_serialize.items():
            common_value = common_value_serialize.get(status)
            current_value = current_value_serialize.get(status) if current_value_serialize.get(status) != 0 else None

            if common_value is None and current_value is None:
                logger.info(f"Отсуствует текущее и общее значение для статуса {status}")
                continue

            ans.append(
                ApplicantValueByStatus(
                    status_id=status, status_name=status_name, current_value=current_value, common_value=common_value
                )
            )

        return ans

    @login_required
    def logout(self) -> None:
        url = f"{self.url_parse}/account/logout"
        resp = self.session.get(url)
        if resp.status_code == 200:
            logger.info("Logout!!!")
