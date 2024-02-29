import logging

from sqlalchemy import insert

from src.config import engine
from src.db.queries import get_all_coworkers_id
from src.db.tables import NewVacancies, AllVacancies
from src.handler.hunt_handler import HuntHandler


def prepare_new_vacancies(arr_vac: list[NewVacancies]):
    handler = HuntHandler()
    # TODO: Добавить динамическое создание столбца
    arr_coworkers_id = get_all_coworkers_id()
    for row_alchemy in arr_vac:
        # TODO: как-то кривовато
        row = {col.name: getattr(row_alchemy, col.name) for col in NewVacancies.__table__.columns}
        log_info = handler.get_log_vacancy(row['id'], row['created'])

        if log_info:
            coworker_info = log_info['account_data']
            if coworker_info['id'] not in arr_coworkers_id:
                handler.update_coworkers(coworker_info)
                arr_coworkers_id.append(coworker_info['id'])
            row['coworkers_id'] = coworker_info['id']
            row['date_last_log'] = log_info['created']
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
            row['date_last_log'] = None

        try:
            stmt = insert(AllVacancies).values(**row)
            with engine.connect() as conn:
                result = conn.execute(stmt)
        except Exception as ex:
            print(ex)
            logging.error(ex)
            continue

    logging.info(f'Get {len(arr_vac)} new vacancies')