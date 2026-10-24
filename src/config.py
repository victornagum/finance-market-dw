import os
from contextlib import contextmanager

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

# NOTE: TrustServerCertificate=yes is acceptable for a local dev server only.
# Use a properly trusted certificate in production.
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


@contextmanager
def db_connection():
    """Open a connection, commit on success, roll back on error, ALWAYS close.

    pyodbc's own `with connection:` commits/rolls back but never closes.
    """
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
