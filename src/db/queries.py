import logging

from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session

from src.config import engine, APPLICANT_STATUSES
from src.db.tables import Coworkers, StatusReasons, AllVacancies, ApplicantsStatus, NewVacancies


def get_all_coworkers_id():
    stmt = select(Coworkers.id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_all_status_vacancy():
    stmt = select(StatusReasons.id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_all_vacancies_id():
    stmt = select(AllVacancies.id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_all_status_applicant():
    stmt = select(ApplicantsStatus.id)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def get_open_vacancy_id():
    stmt = select(AllVacancies.id).where(AllVacancies.state == 'OPEN')
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res


def insert_status_from_json():
    applicant_status_arr = get_all_status_applicant()
    for status_id in APPLICANT_STATUSES:
        if str(status_id) in applicant_status_arr:
            continue
        stmt = insert(ApplicantsStatus).values(id=status_id, name=APPLICANT_STATUSES[status_id])
        with engine.connect() as conn:
            result = conn.execute(stmt)
        applicant_status_arr.append(status_id)


def delete_all_row_new_vacancies():
    stmt = delete(NewVacancies)
    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            logging.info('Delete all rows from new vacancies')
    except Exception:
        logging.error('failed to delete new_vacancies table')


def insert_new_vacancy(row):
    for field in row['additional_fields_list']:
        del row[field]
    stmt = insert(NewVacancies).values(**row)
    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            logging.debug('Insert new vacancy in tmp table')
    except Exception as ex:
        logging.error('failed to insert new_vacancies table')
        logging.error(ex)


def get_all_new_vacancies():
    stmt = select(NewVacancies)
    with Session(engine) as session:
        res = session.execute(stmt).scalars().all()
    return res
