import logging

from airflow.models import TaskInstance
from sqlalchemy import insert
from typing import List, Optional

from src.config import engine
from src.db.queries import get_all_coworkers_id, get_all_vacancies_id, get_open_vacancy_id, get_all_status_applicant, \
    delete_all_row_new_vacancies, insert_new_vacancy, get_all_new_vacancies
from src.db.tables import AllVacancies, ApplicantsStatus, VacStatInfo, NewVacancies
from src.func import prepare_new_vacancies
from src.handler.hunt_handler import HuntHandler
from src.parser.hunt_parser import HuntFlowParser


def get_new_vacancies(ti: TaskInstance, **kwargs) -> Optional[str]:
    handler = HuntHandler()
    new_vac = []
    arr_id_vacancies = get_all_vacancies_id()
    arr_vac = handler.get_all_vacancies()
    delete_all_row_new_vacancies()
    for vac in arr_vac:
        if vac['id'] not in arr_id_vacancies:
            insert_new_vacancy(vac)
            arr_id_vacancies.append(vac['id'])
            new_vac.append(vac)
    if new_vac:
        logging.info(f'Get {len(new_vac)} new vacancy')
        return 'insert_new_vacancies'
    else:
        return None


def add_new_vacancies(ti: TaskInstance, **kwargs):
    arr = get_all_new_vacancies()
    prepare_new_vacancies(arr)


def insert_applicant_status():
    parse = HuntFlowParser(url_parse='https://huntflow.ru',
                           url_api='https://api.huntflow.ru')
    all_status_id = get_all_status_applicant()
    open_vac_id = get_open_vacancy_id()
    try:
        for vac_id in open_vac_id:
            applicant_status_info = parse.get_vacancy_stat_info(vac_id)

            if applicant_status_info is None:
                continue
            items = applicant_status_info.get('items')
            for status_id in items:
                if status_id not in all_status_id:
                    stmt = insert(ApplicantsStatus).values(id=status_id, name=None)
                    with engine.connect() as conn:
                        result = conn.execute(stmt)
                    all_status_id.append(status_id)
                stmt = insert(VacStatInfo).values(vac_id=vac_id,
                                                  status_id=status_id,
                                                  value=items[status_id])
                with engine.connect() as conn:
                    result = conn.execute(stmt)
            logging.info('Add stat info of %s vacancy' % vac_id)
    except Exception as ex:
        logging.error(ex)
        parse.logout()
    finally:
        parse.logout()
