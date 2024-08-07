import logging

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from src.config import engine
from src.db.tables import (
    AllVacancies,
    ApplicantsStatus,
    Coworkers,
    CurrentApplicantValueByStatus,
    NewVacancies,
    VacStatInfo,
)


def get_all_coworkers_id() -> list:
    """
    Идентификаторы всех рекрутеров
    :return:
    """
    stmt = select(Coworkers.id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_all_vacancies_id() -> list:
    """
    Получить идентификаторы всех имеющихся вакансий
    :return:
    """
    stmt = select(AllVacancies.id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_status_applicant(status_id: int) -> list[ApplicantsStatus]:
    """
    Получить имена статусов кандидатов на вакансию
    :return:
    """
    stmt = select(ApplicantsStatus).where(ApplicantsStatus.id == status_id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def delete_all_tmp_vacancies() -> None:
    """
    Удалить все записи из временной таблицы с вакансиями
    :return:
    """
    stmt = delete(NewVacancies)
    try:
        with Session(engine) as session:
            session.execute(stmt)
            session.commit()
            logging.info("Delete all rows from new vacancies")
    except Exception:
        logging.error("failed to delete new_vacancies table")


def insert_tmp_new_vacancy(row) -> None:
    """
    Добавить новую вакансию
    :param row:
    :return:
    """
    for field in row["additional_fields_list"]:
        del row[field]
    stmt = insert(NewVacancies).values(**row)
    try:
        with Session(engine) as session:
            session.execute(stmt)
            session.commit()
            logging.debug("Insert new vacancy in tmp table")
    except Exception as ex:
        logging.error("failed to insert new_vacancies table")
        logging.error(ex)


def get_all_new_vacancies() -> list[NewVacancies]:
    """
    Получить все новые вакансии из временной таблицы
    :return:
    """
    stmt = select(NewVacancies)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_vacancy_besides_state(state: list) -> list[AllVacancies]:
    """
    Получить идентификаторы вакансий по статусу
    :param state: (может быть OPEN, HOLD, CLOSE)
    :return:
    """
    stmt = select(AllVacancies).where(AllVacancies.state not in state)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_last_vacancy_statistic_with_status(
    vac_id: int, status_id: int, table: VacStatInfo | CurrentApplicantValueByStatus
) -> list[VacStatInfo | CurrentApplicantValueByStatus]:
    """
    Проверить есть ли запись по определенному статутусу для вакансии
    :param vac_id:
    :return: True - нужно вставить запись, False - пропустить вакансию
    """
    stmt = (
        select(table)
        .where((table.vac_id == vac_id) & (table.status_id == status_id))
        .order_by(table.date.desc())
        .limit(1)
    )
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()

    return res
