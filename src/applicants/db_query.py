import logging
from datetime import datetime

from sqlalchemy import insert, update
from sqlalchemy.orm import Session

from src.config import engine
from src.db.queries import get_last_vacancy_statistic_with_status, get_status_applicant
from src.db.tables import AllVacancies, ApplicantsStatus, CurrentApplicantValueByStatus, VacStatInfo


logger = logging.getLogger()


def check_status_applicants(status_id: int, status_name: str) -> None:
    """
    Получить идентификатор статуса кандидата
    Если идентификатора нет, то вставляем новую запись со статусом
    :param status_name: название статуса
    :return:
    """
    applicant_status_arr = get_status_applicant(status_id)
    if not applicant_status_arr:
        stmt = insert(ApplicantsStatus).values(id=status_id, name=status_name)
        with Session(engine) as session:
            session.execute(stmt)
            session.commit()


def insert_info_applicant_on_vacancies(
    vac_id: int, status_id: int, value: int, table: VacStatInfo | CurrentApplicantValueByStatus
) -> None:
    """
    Добавление записи вакансии с информацией о статусах кандидатах
    :param vac_id: идентификатор вакансии
    :param vac_info: информация со статусами вакансии
    :return:
    """
    stmt = insert(table).values(vac_id=vac_id, status_id=status_id, value=value, date=datetime.now().date())
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()


def update_info_applicant_on_vacancies(
    db_id: int, status_id: int, value: int, table: VacStatInfo | CurrentApplicantValueByStatus
) -> None:
    """
    Обновление записи со статистикой по вакансии
    """
    stmt = update(table).where(table.id == db_id, table.status_id == status_id).values(value=value)
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()


def handle_applicant_value(
    vacancy: AllVacancies, status_id: int, value: int, table: VacStatInfo | CurrentApplicantValueByStatus
):
    vacancy_stat_info = get_last_vacancy_statistic_with_status(vacancy.id, status_id, table)
    if vacancy_stat_info:
        vac_stat_info = vacancy_stat_info[0]
        if vac_stat_info.date.date() == datetime.now().date():
            text = (
                f"Обновляю запись {vac_stat_info.id} в таблицу "
                "{table.__tablename__} для вакансии {vacancy.id} "
                "со статусом {status_id}"
            )
            logger.info(text)
            update_info_applicant_on_vacancies(
                db_id=vacancy_stat_info[0].id, status_id=status_id, value=value, table=table
            )
            return

    logger.info(
        f"Добавляю новую запись в таблицу {table.__tablename__} для вакансии {vacancy.id} со статусом {status_id}"
    )
    insert_info_applicant_on_vacancies(vac_id=vacancy.id, status_id=status_id, value=value, table=table)
