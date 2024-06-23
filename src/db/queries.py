import logging
from datetime import datetime
from typing import Any, List

from sqlalchemy import delete, func, insert, select
from sqlalchemy.orm import Session

from src.config import engine
from src.db.tables import AllVacancies, ApplicantsStatus, Coworkers, NewVacancies, VacStatInfo


def get_all_coworkers_id() -> List[Any]:
    """
    Идентификаторы всех рекрутеров
    :return:
    """
    stmt = select(Coworkers.id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_all_vacancies_id() -> List[Any]:
    """
    Получить идентификаторы всех имеющихся вакансий
    :return:
    """
    stmt = select(AllVacancies.id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_status_applicant(name: str) -> List[Any]:
    """
    Получить имена статусов кандидатов на вакансию
    :return:
    """
    stmt = select(ApplicantsStatus.id).where(ApplicantsStatus.name == name)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def delete_all_row_new_vacancies() -> None:
    """
    Удалить все записи из временной таблицы с вакансиями
    :return:
    """
    stmt = delete(NewVacancies)
    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            logging.info("Delete all rows from new vacancies")
    except Exception:
        logging.error("failed to delete new_vacancies table")


def insert_new_vacancy(row) -> None:
    """
    Добавить новую вакансию
    :param row:
    :return:
    """
    for field in row["additional_fields_list"]:
        del row[field]
    stmt = insert(NewVacancies).values(**row)
    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            logging.debug("Insert new vacancy in tmp table")
    except Exception as ex:
        logging.error("failed to insert new_vacancies table")
        logging.error(ex)


def get_all_new_vacancies() -> List[NewVacancies]:
    """
    Получить все новые вакансии из временной таблицы
    :return:
    """
    stmt = select(NewVacancies)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_vacancy_id_by_state(state, flg_id=True) -> List[Any]:
    """
    Получить идентификаторы вакансий по статусу
    :param state: (может быть OPEN, HOLD, CLOSE)
    :param flg_id: (только идентификаторы или всю информацию)
    :return:
    """
    if flg_id:
        stmt = select(AllVacancies.id).where(AllVacancies.state == state)
    else:
        stmt = select(AllVacancies).where(AllVacancies.state == state)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def check_vac_in_statistic(vac_id: int) -> bool:
    """
    Проверить последнюю дату по вакансии.
    Если последняя дата совпадает с текущей, то пропустить вакансию
    Если дата не совпадает или вообще нет записи, то нужно добавить строку
    :param vac_id:
    :return: True - нужно вставить запись, False - пропустить вакансию
    """
    stmt = (
        select(VacStatInfo.vac_id, func.max(VacStatInfo.date))
        .where(VacStatInfo.vac_id == vac_id)
        .group_by(VacStatInfo.vac_id)
    )
    with Session(engine) as session:
        res = session.execute(stmt).all()

    if not res:
        return True

    date_today = datetime.today().date()
    date_vac = res[0][1].date()

    if date_today == date_vac:
        return False
    else:
        return True


def get_id_status_applicant(vac_id: int) -> List[Any]:
    stmt = select(VacStatInfo.status_id).where(VacStatInfo.vac_id == vac_id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res
