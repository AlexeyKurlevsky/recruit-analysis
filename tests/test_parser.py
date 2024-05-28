import logging
from src.parser.hunt_parser import HuntFlowParser


def test_login():
    parser = HuntFlowParser()
    try:
        parser.login()
        parser.logout()
    except Exception as ex:
        logging.error(ex)
        parser.get_driver.quit()
