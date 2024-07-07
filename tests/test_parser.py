import logging
from src.applicants.func import check_status_applicants, insert_info_applicant_on_vacancies, update_info_applicant_on_vacancies
from src.db.queries import check_vac_in_statistic, get_all_new_vacancies
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
    statistic = parser.get_vacancy_stat_info(3700192)
    for status_id, name_and_value in statistic.items():
        check_status_applicants(status_id, name_and_value[0])
        vacancy_stat_info = check_vac_in_statistic(3700192, status_id)
        if vacancy_stat_info:
            update_info_applicant_on_vacancies(
                db_id=vacancy_stat_info[0].id, status_id=int(status_id), value=name_and_value[1]
            )
        else:
            insert_info_applicant_on_vacancies(
                vac_id=3700192, status_id=int(status_id), value=name_and_value[1]
            )
    parser.logout()
