import logging

from src.applicants.func import insert_info_open_vacancies
from src.db.queries import get_vacancy_id_by_state
from src.parser.hunt_parser import HuntFlowParser


def insert_info_vacancies() -> None:
    """
    Добавление информации о кандидатов о вакансии
    :return:
    """
    parse = HuntFlowParser()
    arr_vac_id = get_vacancy_id_by_state('OPEN')
    logging.info('Get %s open vacancies' % len(arr_vac_id))
    try:
        for vac_id in arr_vac_id:
            applicant_info = parse.get_vacancy_stat_info(vac_id)
            insert_info_open_vacancies(vac_id, applicant_info)
        parse.logout()
    except Exception as ex:
        logging.error(ex)
        parse.logout()
