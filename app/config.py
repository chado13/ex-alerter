import base64
import json
import os
from os.path import dirname, join
from typing import TypedDict

from dotenv import load_dotenv

basedir = os.path.abspath(dirname(dirname(__file__)))
load_dotenv(join(basedir, ".env"))

WEBHOOK_URI = os.getenv("WEBHOOK", "")