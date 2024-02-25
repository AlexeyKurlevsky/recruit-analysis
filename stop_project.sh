#! /bin/bash

docker compose -f ./postgres-compose.yml stop
docker compose -f ./airflow-compose.yml stop
docker compose -f ./superset-compose.yml stop