import logging
import requests
import json

from functools import cached_property

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

# TODO: убрать в проде HUNTFLOW_REFRESH_TOKEN_DEV
from src.config import HUNTFLOW_USERNAME, HUNTFLOW_PASSWORD, HUNTFLOW_REFRESH_TOKEN_DEV, HUNTFLOW_ACCESS_TOKEN
from src.handler.hunt_handler import HuntHandler
from src.parser.func import get_info_vacancy


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
        handler = HuntHandler(self.url_api, access_token=HUNTFLOW_ACCESS_TOKEN)
        self._org_nick = handler.org_id[1]
        return self._org_nick

    def get_vacancy_stat_info(self, vac_id: int):
        # Парсинг html страницы
        # self._driver.get(f'{self.url_parse}/my/{self._org_nick}/view/vacancy/{vac_id}')
        # try:
        #     WebDriverWait(driver=self._driver, timeout=10).until(
        #         ec.presence_of_element_located((By.CLASS_NAME, 'root--z7B1B'))
        #     )
        # except TimeoutException:
        #     logging.error('vacancy %s not found or page don\'t loading' % vac_id)
        #     return None
        # status_elem = self._driver.find_element(By.CLASS_NAME, 'root--z7B1B')
        # html_text = status_elem.get_attribute('innerHTML')
        # vac_info = get_info_vacancy(html_text)

        cook_drive = self._driver.get_cookies()
        cookies_dict = {}
        for cookie in cook_drive:
            cookies_dict[cookie['name']] = cookie['value']

        resp = requests.get(f'{self.url_parse}/my/{self._org_nick}/vacancy/{vac_id}/stats', cookies=cookies_dict)
        if resp.status_code != 200:
            logging.error('Not stat information about %s vacancy' % vac_id)
            return None

        info = json.loads(resp.content)
        return info

    def logout(self):
        digital_hr_button = self._driver.find_element(By.CLASS_NAME, 'title--b57Ew')
        digital_hr_button.click()
        WebDriverWait(driver=self._driver, timeout=10).until(
            ec.presence_of_element_located((By.XPATH, '//a[@href="/account/logout"]'))
        )
        logout_button = self._driver.find_element(By.XPATH, '//a[@href="/account/logout"]')
        logout_button.click()
        logging.info('Logout from HuntFLow. Goodbye!!!')
