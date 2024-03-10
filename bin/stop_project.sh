#! /bin/bash

docker compose -f ./postgres-compose.yml down
docker compose -f ./airflow-compose.yml down
docker compose -f ./superset-compose.yml down