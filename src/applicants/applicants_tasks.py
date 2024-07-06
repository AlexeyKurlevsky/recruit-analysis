import logging

from airflow.models import TaskInstance

from src.applicants.func import insert_info_applicant_on_vacancies
from src.db.queries import check_vac_in_statistic, get_vacancy_id_by_state
from src.parser.hunt_parser import HuntFlowParser


logger = logging.getLogger()


def insert_info_vacancies(state: str) -> None:
    """
    Добаление информации о кандидатах по вакансиям со стаусом state
    :param state: статус вакансии (OPEN, STATE, CLOSED..)
    :return:
    """
    parse = HuntFlowParser()
    arr_vac_id = get_vacancy_id_by_state(state)
    logging.info("Get %s open vacancies" % len(arr_vac_id))
    try:
        for vac_id in arr_vac_id:
            if check_vac_in_statistic(vac_id):
                applicant_info = parse.get_vacancy_stat_info(vac_id)
                if applicant_info is None:
                    logger.error(f"unable to obtain information about candidates for the vacancy {vac_id}")
                    continue
                insert_info_applicant_on_vacancies(vac_id, applicant_info)
            else:
                continue
        parse.logout()
    except Exception as ex:
        logger.error(ex)
        parse.get_driver.quit()


def update_stat_open_vacancies(ti: TaskInstance, **kwargs) -> None:
    insert_info_vacancies("OPEN")


def update_stat_hold_vacancies(ti: TaskInstance, **kwargs) -> None:
    insert_info_vacancies("HOLD")
