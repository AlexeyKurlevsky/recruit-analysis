from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from src.config import engine, APPLICANT_STATUSES
from src.db.tables import Coworkers, StatusReasons, AllVacancies, ApplicantsStatus


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
