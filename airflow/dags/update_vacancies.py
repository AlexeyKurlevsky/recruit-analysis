import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta

from src.vacancies.vacancy_tasks import update_hold_vacancies, update_open_vacancies

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="update_vacancies",
    catchup=False,
    start_date=datetime.datetime(2024, 1, 27),
    schedule="@hourly",
    max_active_runs=1,
    default_args=default_args,
) as dag:
    hold_vac = PythonOperator(
        task_id="update_hold_vacancies",
        python_callable=update_hold_vacancies,
        provide_context=True,
    )

    open_vac = PythonOperator(
        task_id="update_open_vacancies",
        python_callable=update_open_vacancies,
        provide_context=True,
    )

    hold_vac >> open_vac
