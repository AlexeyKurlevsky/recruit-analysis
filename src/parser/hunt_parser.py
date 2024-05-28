import logging
import requests
import json

from functools import cached_property

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from src.config import (
    HUNTFLOW_USERNAME,
    HUNTFLOW_PASSWORD,
    HUNTFLOW_ACCESS_TOKEN,
    SELENIUM_URL,
    HUNTFLOW_URL,
    HUNTFLOW_URL_API,
    TIME_OUT_LOADING_PAGE,
)
from src.handler.hunt_handler import HuntHandler
from src.parser.func import get_info_vacancy


class HuntFlowParser:
    def __init__(self, url_parse: str = HUNTFLOW_URL, url_api: str = HUNTFLOW_URL_API):
        self.url_parse = url_parse
        self.url_api = url_api
        self._driver = self.get_driver
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
        self._driver = driver
        return self._driver

    def login(self) -> None:
        self._driver.get(f"{self.url_parse}/account/login")
        self._driver.find_element(By.NAME, "email").send_keys(HUNTFLOW_USERNAME)
        self._driver.find_element(By.NAME, "password").send_keys(HUNTFLOW_PASSWORD)
        login_button = self._driver.find_element(
            By.CSS_SELECTOR, "button[data-qa='account-login-submit']"
        )

        # TODO: проверка доступа кнопки
        assert login_button.is_enabled(), "login button is disable"
        login_button.click()

        WebDriverWait(driver=self._driver, timeout=TIME_OUT_LOADING_PAGE).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )

        try:
            errors = self._driver.find_element(By.CLASS_NAME, "error--_ePXW")
            logging.error("Incorrect credentials")
            raise ValueError(errors.text)
        except NoSuchElementException:
            logging.info("Login success!!!")
            self.login_flg = True

    @cached_property
    def get_org_nick(self) -> int:
        handler = HuntHandler(self.url_api, access_token=HUNTFLOW_ACCESS_TOKEN)
        self._org_nick = handler.org_id[1]
        return self._org_nick

    def get_vacancy_stat_info(self, vac_id: int):
        if not self.login_flg:
            self.login()
        self._driver.get(f"{self.url_parse}/my/{self._org_nick}/view/vacancy/{vac_id}")
        try:
            WebDriverWait(driver=self._driver, timeout=TIME_OUT_LOADING_PAGE).until(
                ec.presence_of_element_located((By.CLASS_NAME, "root--z7B1B"))
            )
        except TimeoutException:
            logging.error("vacancy %s not found or page don't loading" % vac_id)
            return None
        status_elem = self._driver.find_element(By.CLASS_NAME, "root--z7B1B")
        html_text = status_elem.get_attribute("innerHTML")
        vac_info = get_info_vacancy(html_text)
        return vac_info

    def logout(self) -> None:
        WebDriverWait(driver=self._driver, timeout=TIME_OUT_LOADING_PAGE).until(
            ec.element_to_be_clickable((By.CLASS_NAME, "title--b57Ew"))
        )
        digital_hr_button = self._driver.find_element(By.CLASS_NAME, "title--b57Ew")
        digital_hr_button.click()
        WebDriverWait(driver=self._driver, timeout=TIME_OUT_LOADING_PAGE).until(
            ec.element_to_be_clickable((By.XPATH, '//a[@href="/account/logout"]'))
        )
        logout_button = self._driver.find_element(
            By.XPATH, '//a[@href="/account/logout"]'
        )
        logout_button.click()
        WebDriverWait(driver=self._driver, timeout=TIME_OUT_LOADING_PAGE).until(
            ec.presence_of_element_located((By.XPATH, '//a[@href="/account/login"]'))
        )
        self._driver.quit()
        logging.info("Logout from HuntFLow. Goodbye!!!")
