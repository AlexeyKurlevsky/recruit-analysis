from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import engine
from src.db.tables import Coworkers, StatusReasons, AllVacancies


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


