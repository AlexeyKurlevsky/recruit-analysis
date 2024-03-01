#! /bin/bash
docker compose -f ./postgres-compose.yml down -v
docker compose -f ./airflow-compose.yml down -v
docker compose -f ./superset-compose.yml down -v

docker rmi $(docker images -a -q)
