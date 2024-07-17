FROM apache/airflow:2.8.1-python3.10

RUN pip install --user poetry==1.8.3

COPY ./pyproject.toml /opt/airflow/pyproject.toml
COPY ./poetry.lock /opt/airflow/poetry.lock

WORKDIR /opt/airflow
RUN poetry install

COPY ./airflow/dags /opt/airflow/dags/
COPY ./src /opt/airflow/dags/src/
COPY ./config /opt/airflow/dags/config
