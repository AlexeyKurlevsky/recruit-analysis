import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta

from src.vacancies.vacancy_tasks import update_not_closed_vacancies

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="update_vacancies",
    catchup=False,
    start_date=datetime.datetime(2024, 1, 27),
    schedule="* 3,6,9,12,15,18,21 * * *",
    max_active_runs=1,
    default_args=default_args,
) as dag:
    update_vacancies = PythonOperator(
        task_id="update_vacancies",
        python_callable=update_not_closed_vacancies,
        provide_context=True,
    )

    update_vacancies
