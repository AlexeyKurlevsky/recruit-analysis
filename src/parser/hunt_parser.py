import logging

from functools import cached_property
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

# TODO: убрать в проде HUNTFLOW_REFRESH_TOKEN_DEV
from src.config import HUNTFLOW_USERNAME, HUNTFLOW_PASSWORD, HUNTFLOW_REFRESH_TOKEN_DEV
from src.handler.handler import HuntHandler


class HuntFlowParser:
    def __init__(self, url_parse: str, url_api: str):
        self.url_parse = url_parse
        self.url_api = url_api
        self._driver = self.get_driver
        self._org_nick = self.get_org_nick

    @cached_property
    def get_driver(self):
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)
        driver.get(f'{self.url_parse}/account/login')

        driver.find_element(By.ID, 'email').send_keys(HUNTFLOW_USERNAME)
        driver.find_element(By.ID, 'password').send_keys(HUNTFLOW_PASSWORD)
        login_button = driver.find_element(By.CSS_SELECTOR, "button[data-qa='account-login-submit']")

        # TODO: проверка доступа кнопки
        assert login_button.is_enabled(), 'login button is disable'
        login_button.click()

        WebDriverWait(driver=driver, timeout=10).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )

        try:
            errors = driver.find_element(By.CLASS_NAME, 'error--_ePXW')
            logging.error('Incorrect credentials')
            raise ValueError(errors.text)
        except NoSuchElementException:
            logging.info('Login success!!!')

        self._driver = driver
        return self._driver

    @cached_property
    def get_org_nick(self):
        handler = HuntHandler(self.url_api, access_token=HUNTFLOW_REFRESH_TOKEN_DEV)
        self._org_nick = handler.org_id[1]
        return self._org_nick

    def get_vacancy_page(self, vac_id: int):
        self._driver.get(f'{self.url_parse}/my/{self._org_nick}/view/vacancy/{vac_id}')

        WebDriverWait(driver= self._driver, timeout=30).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'page-title'))
        )

        try:
            self._driver.find_element(By.CLASS_NAME, 'error-block__title')
            logging.error('Not found of %s vacancy page' % vac_id)
            return None
        except NoSuchElementException:
            logging.info('Get page of %s vacancy' % vac_id)

        status_elem = self._driver.find_element(By.CLASS_NAME, 'root--z7B1B')
        html_elem = status_elem.get_attribute('innerHTML')
        print(html_elem)


