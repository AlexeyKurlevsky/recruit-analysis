import logging
from typing import Optional

from airflow.models import TaskInstance

from src.db.queries import delete_all_tmp_vacancies, get_all_new_vacancies, get_all_vacancies_id, insert_tmp_new_vacancy
from src.handler.hunt_handler import HuntHandler
from src.vacancies.func import insert_new_vacancies, update_vacancy


logger = logging.getLogger()


def get_new_vacancies(ti: TaskInstance, **kwargs) -> str | None:
    """
    Получение новых вакансий
    Логика довольно глупая. Нужно переделать
    Забираем все имеющиеся идентификаторы вакансий из нашей БД,
    забираем все идентификаторы из ХФ. И затем каждый идентификатор из ХФ
    сравниваем с нашим. Проблема, что из ХФ мы получаем вакансии в случайном порядке.
    :param ti:
    :param kwargs:
    :return:
    """
    handler = HuntHandler()
    new_vac = []
    arr_id_vacancies = get_all_vacancies_id()
    arr_vac = handler.get_all_vacancies()
    delete_all_tmp_vacancies()
    for vac in arr_vac:
        if vac["id"] not in arr_id_vacancies:
            insert_tmp_new_vacancy(vac)
            arr_id_vacancies.append(vac["id"])
            new_vac.append(vac)
    if new_vac:
        logger.info(f"Get {len(new_vac)} new vacancy")
        return "insert_new_vacancies"
    return None


def add_new_vacancies(ti: TaskInstance, **kwargs) -> None:
    """
    Добавить новые вакансии
    :param ti:
    :param kwargs:
    :return:
    """
    arr = get_all_new_vacancies()
    insert_new_vacancies(arr)


def update_not_closed_vacancies(ti: TaskInstance, **kwargs) -> None:
    """
    Обновление всех вакансий кроме статуса closed
    В аргумент передается статус, который не нужно обновлять
    """
    update_vacancy(["CLOSED"])
