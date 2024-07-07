import logging

from airflow.models import TaskInstance

from src.applicants.func import (
    check_status_applicants,
    insert_info_applicant_on_vacancies,
    update_info_applicant_on_vacancies,
)
from src.db.queries import check_vac_in_statistic, get_vacancy_besides_state
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
            for status_id, name_and_value in applicant_info.items():
                check_status_applicants(status_id, name_and_value[0])
                logger.info(f"Проверяю запись для вакансии {vacancy.id} по статусу {status_id}")
                vacancy_stat_info = check_vac_in_statistic(vacancy.id, status_id)
                if vacancy_stat_info:
                    logger.info(
                        f"Обновляю запись {vacancy_stat_info[0].id} для вакансии {vacancy.id} со статусом {status_id}"
                    )
                    update_info_applicant_on_vacancies(
                        db_id=vacancy_stat_info[0].id, status_id=int(status_id), value=name_and_value[1]
                    )
                else:
                    logger.info(f"Добавляю новую запись для вакансии {vacancy.id} со статусом {status_id}")
                    insert_info_applicant_on_vacancies(
                        vac_id=vacancy.id, status_id=int(status_id), value=name_and_value[1]
                    )
        parse.logout()
    except Exception as ex:
        logger.error(ex)
        parse.logout()
