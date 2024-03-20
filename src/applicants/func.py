from sqlalchemy import insert, update

from src.config import engine
from src.db.queries import get_status_applicant, get_id_status_applicant
from src.db.tables import ApplicantsStatus, VacStatInfo


def check_status_applicants(status_name: str) -> int:
    """
    Получить идентификатор статуса кандидата
    Если идентификатора нет, то вставляем новую запись со статусом
    :param status_name: название статуса
    :return:
    """
    applicant_status_arr = get_status_applicant(status_name)
    if not applicant_status_arr:
        stmt = insert(ApplicantsStatus).values(name=status_name)
        with engine.connect() as conn:
            result = conn.execute(stmt)
            key = result.inserted_primary_key
        return key[0]
    else:
        return applicant_status_arr[0]


def insert_info_applicant_on_vacancies(vac_id: int, vac_info: dict) -> None:
    """
    Добавление записи вакансии с информацией о статусах кандидатах
    :param vac_id: идентификатор вакансии
    :param vac_info: информация со статусами вакансии
    :return:
    """
    for status_name in vac_info:
        status_id = check_status_applicants(status_name)
        stmt = insert(VacStatInfo).values(
            vac_id=vac_id, status_id=status_id, value=vac_info[status_name]
        )
        with engine.connect() as conn:
            result = conn.execute(stmt)


def update_info_applicant_on_vacancies(vac_id: int, vac_info: dict) -> None:
    """
    Обновление записи вакансии с информацией о статусах кандидатах
    :param vac_id:
    :param vac_info:
    :return:
    """
    for status_name in vac_info:
        status_id = check_status_applicants(status_name)
        # TODO: можно поставить условие если значение изменилось, то тогда обновлять
        status_arr = get_id_status_applicant(vac_id)
        if status_id in status_arr:
            stmt = (
                update(VacStatInfo)
                .where(VacStatInfo.status_id == status_id, VacStatInfo.vac_id == vac_id)
                .values(value=vac_info[status_name])
            )
        else:
            stmt = insert(VacStatInfo).values(
                vac_id=vac_id, status_id=status_id, value=vac_info[status_name]
            )
        with engine.connect() as conn:
            result = conn.execute(stmt)
