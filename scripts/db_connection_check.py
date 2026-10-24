import sys
from pathlib import Path

import pyodbc

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from config import db_connection

try:
    with db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT DB_NAME();")
        print("Connection successful!")
        print("Connected database:", cursor.fetchone()[0])
except pyodbc.Error as error:
    print("Connection failed:")
    print(error)