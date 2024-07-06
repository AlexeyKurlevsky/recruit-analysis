import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta

from src.applicants.applicants_tasks import update_statistic_vacancies

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="statistic_applicant",
    catchup=False,
    start_date=datetime.datetime(2024, 1, 27),
    schedule="30 0 * * *",
    max_active_runs=1,
    default_args=default_args,
) as dag:

    open_vac = PythonOperator(
        task_id="update_open_vacancies",
        python_callable=update_statistic_vacancies,
        provide_context=True,
    )
