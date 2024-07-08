import logging
from src.db.tables import AllVacancies
from src.applicants.utils import handle_vacancy_with_status
from src.db.queries import get_last_vacancy_statistic_with_status, get_all_new_vacancies
from src.parser.hunt_parser import HuntFlowParser
from requests import session

from src.vacancies.func import insert_new_vacancies, update_vacancy
from src.vacancies.vacancy_tasks import get_new_vacancies

# def test_add_new_vacancy():
#     get_new_vacancies("sdcvsd")
#     arr = get_all_new_vacancies()


# def test_update_vacancies():
#     update_vacancy(["CLOSED"])


def test_login():
    parser = HuntFlowParser()
    vacancy = AllVacancies()
    vacancy.id = 3700192
    vacancy.position = "test_position"
    statistic = parser.get_vacancy_stat_info(vacancy.id)
    if statistic is None:
        raise ValueError("Не смог получить информацию по статистике вакансии")
    handle_vacancy_with_status(applicant_info=statistic, vacancy=vacancy)
    parser.logout()
