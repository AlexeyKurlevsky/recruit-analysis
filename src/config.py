import os
import logging

from dotenv import load_dotenv

load_dotenv()

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

HUNTFLOW_ACCESS_TOKEN = os.getenv('HUNTFLOW_ACCESS_TOKEN')
HUNTFLOW_REFRESH_TOKEN = os.getenv('HUNTFLOW_REFRESH_TOKEN')

