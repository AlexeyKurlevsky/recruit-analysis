import logging

from airflow.models import TaskInstance

from src.applicants.utils import handle_vacancy_with_status
from src.db.queries import get_vacancy_besides_state
from src.parser.hunt_parser import HuntFlowParser


logger = logging.getLogger()


def update_statistic_vacancies(ti: TaskInstance, **kwargs) -> None:
    parse = HuntFlowParser()
    vacancies = get_vacancy_besides_state(["CLOSED"])
    logging.info(f"Get {len(vacancies)} open vacancies")
    try:
        for vacancy in vacancies:
            logger.info(f"Хочу получить информацию по статусам вакансии {vacancy.id}")
            applicant_info = parse.get_vacancy_stat_info(vacancy.id)
            if applicant_info is None:
                logger.error(f"unable to obtain information about candidates for the vacancy {vacancy.id}")
                continue
            handle_vacancy_with_status(applicant_info=applicant_info, vacancy=vacancy)
        parse.logout()
    except Exception as ex:
        logger.error(ex)
        parse.logout()
