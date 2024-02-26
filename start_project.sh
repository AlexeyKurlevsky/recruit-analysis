#! /bin/bash

mkdir -p ./dags ./logs ./plugins ./config
echo "AIRFLOW_UID=$(id -u)" >> .env

docker compose -f ./postgres-compose.yml up -d
#docker compose -f ./airflow-compose.yml up -d --build
docker compose -f ./superset-compose.yml up -d