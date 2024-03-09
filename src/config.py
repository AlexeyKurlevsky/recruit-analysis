import os
import logging
import json

from airflow import AirflowException
from dotenv import load_dotenv
from sqlalchemy import create_engine
from airflow.settings import DAGS_FOLDER
from airflow.models import Variable

load_dotenv()

FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)

# Для разработки
HUNTFLOW_ACCESS_TOKEN = os.getenv("HUNTFLOW_ACCESS_TOKEN")
HUNTFLOW_REFRESH_TOKEN = os.getenv("HUNTFLOW_REFRESH_TOKEN")

# HUNTFLOW_ACCESS_TOKEN = Variable.get("HUNTFLOW_ACCESS_TOKEN")
# HUNTFLOW_REFRESH_TOKEN = Variable.get("HUNTFLOW_REFRESH_TOKEN")

if HUNTFLOW_ACCESS_TOKEN is None or HUNTFLOW_REFRESH_TOKEN is None:
    raise AirflowException('Set HUNTFLOW_ACCESS_TOKEN or HUNTFLOW_REFRESH_TOKEN')

HUNTFLOW_USERNAME = os.getenv("HUNTFLOW_USERNAME")
HUNTFLOW_PASSWORD = os.getenv("HUNTFLOW_PASSWORD")

DATABASE_HOST = os.getenv("HUNTFLOW_DATABASE_HOST")
DATABASE_PORT = os.getenv("HUNTFLOW_DATABASE_PORT")
DATABASE_HUNTFLOW = os.getenv("HUNTFLOW_DATABASE_DB")
DATABASE_HUNTFLOW_USERNAME = os.getenv("HUNTFLOW_DATABASE_USERNAME")
DATABASE_HUNTFLOW_PASSWORD = os.getenv("HUNTFLOW_DATABASE_PASSWORD")

SQLALCHEMY_DB_URI = (
    f"postgresql+psycopg2://"
    f"{DATABASE_HUNTFLOW_USERNAME}:{DATABASE_HUNTFLOW_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_HUNTFLOW}"
)

MAX_ITEM_ON_PAGE = 50
try:
    f = open("./config/applicant_statuses.json")
except FileNotFoundError:
    f = open(f"{DAGS_FOLDER}/config/applicant_statuses.json")
applicant_statuses = json.load(f)
APPLICANT_STATUSES = {elem["id"]: elem["name"] for elem in applicant_statuses}

engine = create_engine(SQLALCHEMY_DB_URI)
