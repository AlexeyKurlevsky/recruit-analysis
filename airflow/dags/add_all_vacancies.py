import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import timedelta

from src.task import get_new_vacancies, add_new_vacancies

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    catchup=False,
    dag_id="add_all_vacancies",
    start_date=datetime.datetime(2024, 1, 27),
    schedule="@daily",
    max_active_runs=1,
    default_args=default_args,
) as dag:
    get_all_vac_from_hf = BranchPythonOperator(
        task_id="get_new_vacancies",
        python_callable=get_new_vacancies,
        provide_context=True,
    )

    insert_new_vacancies = PythonOperator(
        task_id="insert_new_vacancies",
        python_callable=add_new_vacancies,
        provide_context=True,
    )

    get_all_vac_from_hf >> insert_new_vacancies
