import logging

from selenium import webdriver
from functools import cached_property

from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from src.config import HUNTFLOW_USERNAME, HUNTFLOW_PASSWORD


class HuntFlowParser:
    def __init__(self, url: str):
        self.url = url
        self.driver = self.get_driver

    @cached_property
    def get_driver(self):
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)
        driver.get(f'{self.url}/account/login')

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

        self.driver = driver
        return self.driver

