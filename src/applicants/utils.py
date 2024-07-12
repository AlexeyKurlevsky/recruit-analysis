import logging

from src.applicants.db_query import check_status_applicants, handle_applicant_value
from src.db.tables import AllVacancies, CurrentApplicantValueByStatus, VacStatInfo
from src.parser.data_serialiaze import ApplicantValueByStatus


logger = logging.getLogger()


def handle_vacancy_with_status(applicant_info: list[ApplicantValueByStatus], vacancy: AllVacancies):
    for status in applicant_info:
        check_status_applicants(status.status_id, status.status_name)
        logger.info(f"Проверяю запись для вакансии {vacancy.id} по статусу {status.status_id}")

        if status.common_value is not None:
            handle_applicant_value(vacancy, status.status_id, status.common_value, VacStatInfo)

        if status.current_value is not None:
            handle_applicant_value(vacancy, status.status_id, status.current_value, CurrentApplicantValueByStatus)
