import os
import logging


class Config:

    BASE_DIR = os.getcwd()
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    SCREENSHOT_DIR = os.path.join(BASE_DIR, 'screenshots')

    DRIVER_PATH = None
    LOG_LEVEL = logging.INFO
