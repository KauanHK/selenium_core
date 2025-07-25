import os
from datetime import datetime
import logging


class Config:

    BASE_DIR = os.getcwd()
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    SCREENSHOT_DIR = os.path.join(BASE_DIR, 'screenshots')

    LOG_FILE_PATH = os.path.join(LOG_DIR, f'{datetime.now().strftime("%d-%m-%Y_%H-%M")}.log')
    DRIVER_PATH = None

    LOG_LEVEL = logging.INFO
