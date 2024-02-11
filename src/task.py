import logging

from sqlalchemy.orm import Session
from sqlalchemy import insert, select

from src.config import engine
from src.db.queries import get_all_coworkers_id, get_all_status_vacancy, get_all_vacancies_id
from src.db.tables import AllVacancies, Coworkers
from src.func import remove_additional_column
from src.handler import HuntHandler


def get_new_vacancies():
    handler = HuntHandler()
    new_vac = []
    arr_id_vacancies = get_all_vacancies_id()

    arr_vac = handler.get_all_vacancies()
    for vac in arr_vac:
        if vac['id'] not in arr_id_vacancies:
            new_vac.append(vac)

    return new_vac


def prepare_new_vacancies(arr_vac):
    handler = HuntHandler()
    # TODO: Добавить динамическое создание столбца
    arr_coworkers_id = get_all_coworkers_id()
    for row in arr_vac:
        row = remove_additional_column(row, handler.additional_fields)
        log_info = handler.get_log_vacancy(row['id'], row['created'])

        if log_info:
            coworker_info = log_info['account_data']
            if coworker_info['id'] not in arr_coworkers_id:
                handler.update_coworkers(coworker_info)
                arr_coworkers_id.append(coworker_info['id'])
            row['coworkers_id'] = coworker_info['id']
            # Если понадобятся статусы
            # if log_info['account_vacancy_hold_reason']:
            #     row['reason_id'] = log_info['account_vacancy_hold_reason']
            #     if log_info['account_vacancy_hold_reason'] not in arr_status_id:
            #         status = ('hold', log_info['account_vacancy_hold_reason'])
            #         handler.update_status_reasons(status)
            #         arr_status_id.append(log_info['account_vacancy_hold_reason'])
            # elif log_info['account_vacancy_close_reason']:
            #     row['reason_id'] = log_info['account_vacancy_close_reason']
            #     if log_info['account_vacancy_close_reason'] not in arr_status_id:
            #         status = ('close', log_info['account_vacancy_close_reason'])
            #         handler.update_status_reasons(status)
            #         arr_status_id.append(log_info['account_vacancy_close_reason'])
            # else:
            #     row['reason_id'] = None

            if row['state'] == 'CLOSED':
                row['date_closed'] = log_info['created']
                row['flg_close_recruiter'] = handler.check_reason_close(row['id'])
            else:
                row['flg_close_recruiter'] = False

        else:
            row['coworkers_id'] = None
            row['reason_id'] = None
            row['date_closed'] = None
            row['flg_close_recruiter'] = False

        try:
            stmt = insert(AllVacancies).values(**row)
            with engine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()
        except Exception as ex:
            logging.error(ex)
            continue

    logging.info(f'Get {len(arr_vac)} new vacancies')
