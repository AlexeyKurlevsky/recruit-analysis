from sqlalchemy import insert, update
from sqlalchemy.orm import Session

from src.config import engine
from src.db.queries import get_status_applicant
from src.db.tables import ApplicantsStatus, VacStatInfo


def check_status_applicants(status_id: str, status_name: str) -> None:
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


def insert_info_applicant_on_vacancies(vac_id: int, status_id: int, value: int) -> None:
    """
    Добавление записи вакансии с информацией о статусах кандидатах
    :param vac_id: идентификатор вакансии
    :param vac_info: информация со статусами вакансии
    :return:
    """
    stmt = insert(VacStatInfo).values(vac_id=vac_id, status_id=status_id, value=value)
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()


def update_info_applicant_on_vacancies(db_id: int, status_id: int, value: int) -> None:
    """
    Обновление записи со статистикой по вакансии
    """
    stmt = update(VacStatInfo).where(VacStatInfo.id == db_id, VacStatInfo.status_id == status_id).values(value=value)
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()
