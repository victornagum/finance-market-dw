import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

# Validate required configuration
if not DB_SERVER:
    raise ValueError("Missing required environment variable: DB_SERVER")

if not DB_NAME:
    raise ValueError("Missing required environment variable: DB_NAME")

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={DB_SERVER};"
    f"DATABASE={DB_NAME};"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


def get_connection():
    return pyodbc.connect(CONNECTION_STRING)