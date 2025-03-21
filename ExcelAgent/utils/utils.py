import os
import logging
import base64
import requests
import time


def get_logger(scope):
    logger = logging.getLogger(scope)

    # if os.environ["APP_ENV"] in ["local", "dev", "stage"]:
    #     logging.basicConfig(level=logging.DEBUG)
    # else:
    logging.basicConfig(level=logging.INFO)

    return logger

logger = get_logger(__name__)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
