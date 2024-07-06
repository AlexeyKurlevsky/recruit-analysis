import logging
from src.db.queries import get_all_new_vacancies
from src.parser.hunt_parser import HuntFlowParser

from src.vacancies.func import insert_new_vacancies, update_vacancy
from src.vacancies.vacancy_tasks import get_new_vacancies

def test_add_new_vacancy():
    get_new_vacancies("sdcvsd")
    arr = get_all_new_vacancies()


def test_update_vacancies():
    update_vacancy(["CLOSED"])



# def test_login():
#     parser = HuntFlowParser()
#     try:
#         parser.login()
#         parser.logout()
#     except Exception as ex:
#         logging.error(ex)
#         parser.get_driver.quit()
