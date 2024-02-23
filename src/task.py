import logging

from sqlalchemy import insert

from src.config import engine
from src.db.queries import get_all_coworkers_id, get_all_vacancies_id, get_open_vacancy_id, get_all_status_applicant
from src.db.tables import AllVacancies, ApplicantsStatus, VacStatInfo
from src.handler.func import remove_additional_column
from src.handler.hunt_handler import HuntHandler
from src.parser.hunt_parser import HuntFlowParser


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


def insert_applicant_status():
    parse = HuntFlowParser(url_parse='https://huntflow.ru',
                           url_api='https://api.huntflow.ru')
    all_status_id = get_all_status_applicant()
    open_vac_id = get_open_vacancy_id()
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
                    conn.commit()
                all_status_id.append(status_id)
            stmt = insert(VacStatInfo).values(vac_id=vac_id,
                                              status_id=status_id,
                                              value=items[status_id])
            with engine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()
        logging.info('Add stat info of %s vacancy' % vac_id)
