
import pyodbc

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=VPN-CHUWI;"
    "DATABASE=FinanceDW;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

try:
    with pyodbc.connect(connection_string, timeout=10) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT DB_NAME();")

        database_name = cursor.fetchone()[0]

        print("Connection successful!")
        print("Connected database:", database_name)

except pyodbc.Error as error:
    print("Connection failed:")
    print(error)
