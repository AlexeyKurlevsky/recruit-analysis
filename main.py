import asyncio

from src.task import get_new_vacancies, prepare_new_vacancies

if __name__ == '__main__':
    arr_vac = get_new_vacancies()
    new_vacancies = prepare_new_vacancies(arr_vac)
