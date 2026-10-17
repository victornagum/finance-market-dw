
import pyodbc

from config import get_connection

try:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT DB_NAME();")

        database_name = cursor.fetchone()[0]

        print("Connection successful!")
        print("Connected database:", database_name)

except pyodbc.Error as error:
    print("Connection failed:")
    print(error)
