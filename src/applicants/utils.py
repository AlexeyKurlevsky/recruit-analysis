import logging
from datetime import datetime

from src.applicants.db_query import (
    check_status_applicants,
    insert_info_applicant_on_vacancies,
    update_info_applicant_on_vacancies,
)
from src.db.queries import get_last_vacancy_statistic_with_status
from src.db.tables import AllVacancies


logger = logging.getLogger()


def handle_vacancy_with_status(applicant_info: dict[str, tuple[str, int]], vacancy: AllVacancies):
    for status_id, name_and_value in applicant_info.items():
        check_status_applicants(int(status_id), name_and_value[0])
        logger.info(f"Проверяю запись для вакансии {vacancy.id} по статусу {status_id}")
        vacancy_stat_info = get_last_vacancy_statistic_with_status(vacancy.id, int(status_id))
        if vacancy_stat_info:
            vac_stat_info = vacancy_stat_info[0]
            if vac_stat_info.date.date() == datetime.now().date():
                logger.info(f"Обновляю запись {vac_stat_info.id} для вакансии {vacancy.id} со статусом {status_id}")
                update_info_applicant_on_vacancies(
                    db_id=vacancy_stat_info[0].id, status_id=int(status_id), value=name_and_value[1]
                )
                continue
        logger.info(f"Добавляю новую запись для вакансии {vacancy.id} со статусом {status_id}")
        insert_info_applicant_on_vacancies(vac_id=vacancy.id, status_id=int(status_id), value=name_and_value[1])
