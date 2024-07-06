import logging
from functools import cached_property

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from src.config import (
    HUNTFLOW_ACCESS_TOKEN,
    HUNTFLOW_PASSWORD,
    HUNTFLOW_URL,
    HUNTFLOW_URL_API,
    HUNTFLOW_USERNAME,
    SELENIUM_URL,
    TIME_OUT_LOADING_PAGE,
)
from src.handler.hunt_handler import HuntHandler
from src.parser.func import get_info_vacancy


logger = logging.getLogger()


class HuntFlowParser:
    def __init__(self, url_parse: str = HUNTFLOW_URL, url_api: str = HUNTFLOW_URL_API):
        self.url_parse = url_parse
        self.url_api = url_api
        self.driver = self.get_driver
        self._org_nick = self.get_org_nick
        self.login_flg = False

    @cached_property
    def get_driver(self) -> WebDriver:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--start-maximized")
        driver = webdriver.Remote(f"{SELENIUM_URL}/wd/hub", options=options)
        self.driver = driver
        return self.driver

    def login(self) -> None:
        self.driver.get(f"{self.url_parse}/account/login")
        self.driver.find_element(By.NAME, "email").send_keys(HUNTFLOW_USERNAME)
        self.driver.find_element(By.NAME, "password").send_keys(HUNTFLOW_PASSWORD)
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-qa='account-login-submit']")

        # TODO: проверка доступа кнопки
        assert login_button.is_enabled(), "login button is disable"
        login_button.click()

        WebDriverWait(driver=self.driver, timeout=TIME_OUT_LOADING_PAGE).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )

        try:
            errors = self.driver.find_element(By.CLASS_NAME, "error--_ePXW")
            logger.error("Incorrect credentials")
            raise ValueError(errors.text)
        except NoSuchElementException:
            logger.info("Login success!!!")
            self.login_flg = True

    @cached_property
    def get_org_nick(self) -> str:
        handler = HuntHandler(self.url_api, access_token=HUNTFLOW_ACCESS_TOKEN)
        self._org_nick = handler.org_id[1]
        return self._org_nick

    def get_vacancy_stat_info(self, vac_id: int) -> dict[str, int] | None:
        if not self.login_flg:
            self.login()
        self.driver.get(f"{self.url_parse}/my/{self._org_nick}/view/vacancy/{vac_id}")
        try:
            WebDriverWait(driver=self.driver, timeout=TIME_OUT_LOADING_PAGE).until(
                ec.presence_of_element_located((By.CLASS_NAME, "root--z7B1B"))
            )
        except TimeoutException:
            logger.error(f"vacancy {vac_id} not found or page don't loading")
            return None
        status_elem = self.driver.find_element(By.CLASS_NAME, "root--z7B1B")
        html_text = status_elem.get_attribute("innerHTML")
        if html_text:
            vac_info = get_info_vacancy(html_text)
            return vac_info
        logger.error("Dont get applicants status")
        return None

    def logout(self) -> None:
        WebDriverWait(driver=self.driver, timeout=TIME_OUT_LOADING_PAGE).until(
            ec.element_to_be_clickable((By.CLASS_NAME, "title--b57Ew"))
        )
        digital_hr_button = self.driver.find_element(By.CLASS_NAME, "title--b57Ew")
        digital_hr_button.click()
        WebDriverWait(driver=self.driver, timeout=TIME_OUT_LOADING_PAGE).until(
            ec.element_to_be_clickable((By.XPATH, '//a[@href="/account/logout"]'))
        )
        logout_button = self.driver.find_element(By.XPATH, '//a[@href="/account/logout"]')
        logout_button.click()
        WebDriverWait(driver=self.driver, timeout=TIME_OUT_LOADING_PAGE).until(
            ec.presence_of_element_located((By.XPATH, '//a[@href="/account/login"]'))
        )
        self.driver.quit()
        logger.info("Logout from HuntFLow. Goodbye!!!")
