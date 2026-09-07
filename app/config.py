import os

from dotenv import load_dotenv

load_dotenv()


APP_NAME = os.getenv(
    "APP_NAME",
    "SAP Cloud ALM AI Copilot",
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "0.1.0",
)
