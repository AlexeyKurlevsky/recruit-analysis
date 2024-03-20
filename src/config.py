import os
import logging
import json

from airflow import AirflowException
from dotenv import load_dotenv
from sqlalchemy import create_engine
from airflow.settings import DAGS_FOLDER
from airflow.models import Variable


def check_huntflow_token(dict_token: dict):
    for key in dict_token:
        if dict_token[key] is None or dict_token[key] == "CHANGE_ME":
            raise AirflowException(f"Set {key}")


load_dotenv()

FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)

# Для разработки
# HUNTFLOW_ACCESS_TOKEN = os.getenv("HUNTFLOW_ACCESS_TOKEN")
# HUNTFLOW_REFRESH_TOKEN = os.getenv("HUNTFLOW_REFRESH_TOKEN")

HUNTFLOW_ACCESS_TOKEN = Variable.get("HUNTFLOW_ACCESS_TOKEN")
HUNTFLOW_REFRESH_TOKEN = Variable.get("HUNTFLOW_REFRESH_TOKEN")

tokens = {
    "HUNTFLOW_ACCESS_TOKEN": HUNTFLOW_ACCESS_TOKEN,
    "HUNTFLOW_REFRESH_TOKEN": HUNTFLOW_REFRESH_TOKEN,
}

check_huntflow_token(tokens)

HUNTFLOW_USERNAME = os.getenv("HUNTFLOW_USERNAME")
HUNTFLOW_PASSWORD = os.getenv("HUNTFLOW_PASSWORD")
HUNTFLOW_URL = os.getenv("HUNTFLOW_URL", "https://huntflow.ru")
HUNTFLOW_URL_API = os.getenv("HUNTFLOW_URL_API", "https://api.huntflow.ru")

DATABASE_HOST = os.getenv("HUNTFLOW_DATABASE_HOST")
DATABASE_PORT = os.getenv("HUNTFLOW_DATABASE_PORT")
DATABASE_HUNTFLOW = os.getenv("HUNTFLOW_DATABASE_DB")
DATABASE_HUNTFLOW_USERNAME = os.getenv("HUNTFLOW_DATABASE_USERNAME")
DATABASE_HUNTFLOW_PASSWORD = os.getenv("HUNTFLOW_DATABASE_PASSWORD")

SELENIUM_URL = os.getenv("SELENIUM_URL", "http://remote_chromedriver:4444")

SQLALCHEMY_DB_URI = (
    f"postgresql+psycopg2://"
    f"{DATABASE_HUNTFLOW_USERNAME}:{DATABASE_HUNTFLOW_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_HUNTFLOW}"
)

MAX_ITEM_ON_PAGE = 50
TIME_OUT_LOADING_PAGE = 30
try:
    f = open("./config/applicant_statuses.json")
except FileNotFoundError:
    f = open(f"{DAGS_FOLDER}/config/applicant_statuses.json")
applicant_statuses = json.load(f)
APPLICANT_STATUSES = {elem["id"]: elem["name"] for elem in applicant_statuses}

engine = create_engine(SQLALCHEMY_DB_URI)
