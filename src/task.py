import logging

from sqlalchemy.orm import Session
from sqlalchemy import insert

from src.config import engine
from src.db.tables import AllVacancies, Coworkers
from src.func import check_new_row, remove_additional_column
from src.handler import HuntHandler


def insert_new_vacancies():
    handler = HuntHandler()
    session = Session(bind=engine)
    rows = session.query(AllVacancies).count()
    diff = handler.total_vacancy - rows

    if diff <= 0:
        logging.info('all vacancies added')
        return None

    path = f'accounts/{handler.org_id}/vacancies'
    arr_vac = check_new_row(diff, handler, path)
    # TODO: Добавить динамическое создание столбца
    arr_vac = [remove_additional_column(elem, handler.additional_fields) for elem in arr_vac]

    for row in arr_vac:
        stmt = insert(AllVacancies).values(**row)
        with engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

    logging.info(f'Get {len(arr_vac)} new vacancies')


def add_all_coworkers():
    handler = HuntHandler()
    session = Session(bind=engine)
    rows = session.query(Coworkers).count()
    diff = handler.total_coworkers - rows

    if diff <= 0:
        logging.info('all vacancies added')
        return None

    path = f'accounts/{handler.org_id}/coworkers'
    arr_cow = check_new_row(diff, handler, path)

    for row in arr_cow:
        stmt = insert(Coworkers).values(id=row['id'],
                                        member=row['member'],
                                        name=row['name'],
                                        type=row['type'])
        with engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

    logging.info(f'Get {len(arr_cow)} new coworkers')
