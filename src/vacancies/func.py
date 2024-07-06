import logging

from sqlalchemy import update
from sqlalchemy.orm import Session

from src.config import engine
from src.db.queries import get_all_coworkers_id, get_vacancy_besides_state
from src.db.tables import AllVacancies, NewVacancies
from src.handler.hunt_handler import HuntHandler


logger = logging.getLogger()


def create_new_vacancy_from_api_data(data: dict) -> AllVacancies:
    new_vacancy = AllVacancies()
    new_vacancy.id = data["id"]
    new_vacancy.account_division = data["account_division"]
    new_vacancy.account_region = data["account_region"]
    new_vacancy.position = data["position"]
    new_vacancy.company = data["company"]
    new_vacancy.money = data["money"]
    new_vacancy.priority = data["priority"]
    new_vacancy.hidden = data["hidden"]
    new_vacancy.state = data["state"]
    new_vacancy.created = data["created"]
    new_vacancy.additional_fields_list = data["additional_fields_list"]
    new_vacancy.multiple = data["multiple"]
    new_vacancy.parent = data["parent"]
    new_vacancy.account_vacancy_status_group = data["account_vacancy_status_group"]
    return new_vacancy


def insert_new_vacancies(arr_vac: list[NewVacancies]) -> None:
    """
    Вставить новые вакансии
    :param arr_vac: Список новых вакансий
    :return:
    """
    handler = HuntHandler()
    arr_coworkers_id = get_all_coworkers_id()
    for row in arr_vac:
        data_vacancy = handler.get_vacancy_data(row.id)
        if not data_vacancy:
            logger.error(f"don't get data about vacany {row.id}")
            continue

        new_vacancy = create_new_vacancy_from_api_data(data_vacancy)

        log_info = handler.get_log_vacancy(row.id, row.created)

        if log_info:
            coworker_info = log_info["account_data"]
            if coworker_info["id"] not in arr_coworkers_id:
                handler.update_coworkers(coworker_info)
                arr_coworkers_id.append(coworker_info["id"])
            new_vacancy.coworkers_id = coworker_info["id"]
            new_vacancy.date_last_log = log_info["created"]

            if new_vacancy.state == "CLOSED":
                new_vacancy.date_closed = log_info["created"]
                new_vacancy.flg_close_recruiter = handler.check_reason_close(new_vacancy.id)
            else:
                new_vacancy.flg_close_recruiter = False

        else:
            new_vacancy.coworkers_id = None
            new_vacancy.date_closed = None
            new_vacancy.flg_close_recruiter = False
            new_vacancy.date_last_log = None

        try:
            with Session(engine) as session:
                session.add(new_vacancy)
                session.commit()
        except Exception as ex:
            logger.error(ex)
            continue

    logger.info(f"Get {len(arr_vac)} new vacancies")


def update_vacancy(state: list[str]):
    """
    Обновление всех вакансий с определенным статусом
    К примеру, обновляем вакансии, у которых статус OPEN
    Если у вакансии изменился статус, то происходит обновление по последнему логу
    :param state: (OPEN, HOLD, CLOSE...)
    :return:
    """
    handler = HuntHandler()
    vacancies = get_vacancy_besides_state(state)
    arr_coworkers_id = get_all_coworkers_id()
    cnt = 0
    for vac in vacancies:
        update_var = {}
        vacancy_data = handler.get_vacancy_data(vac.id)
        if not vacancy_data:
            logger.error(f"Dont get data vacancy {vac.id}")
            continue

        log_info = handler.get_log_vacancy(vac.id, vac.created)
        if not log_info:
            logger.error(f"Dont get log vacancy {vac.id}")
            continue

        coworker_info = log_info["account_data"]
        if coworker_info["id"] not in arr_coworkers_id:
            handler.update_coworkers(coworker_info)
            arr_coworkers_id.append(coworker_info["id"])

        update_var["coworkers_id"] = coworker_info["id"]
        update_var["date_last_log"] = log_info["created"]
        update_var["state"] = vacancy_data["state"]

        if log_info["state"] == "CLOSED":
            update_var["date_closed"] = log_info["created"]
            update_var["flg_close_recruiter"] = handler.check_reason_close(vac.id)

        try:
            stmt = update(AllVacancies).values(update_var).where(AllVacancies.id == vac.id)
            with Session(engine) as session:
                session.execute(stmt)
                session.commit()
                logger.info(f"Update {vac.id} vacancy")
                cnt += 1
        except Exception as ex:
            logger.error(ex)
            continue
    logger.info(f"Update {cnt} vacancies")
