import json
import pyodbc

from extract import fetch_market_data

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=VPN-CHUWI;"
    "DATABASE=FinanceDW;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


insert_sql = """
    INSERT INTO raw.ApiResponse (
        SourceName,
        Endpoint,
        RequestParams,
        ResponseJson
    )
    VALUES (?, ?, ?, ?);
"""

endpoint, request_params, data = fetch_market_data()

response_json = json.dumps(data)
request_params_json = json.dumps(request_params)

values = (
    "Binance",
    endpoint,
    request_params_json,
    response_json
)


with pyodbc.connect(connection_string) as connection:
    cursor = connection.cursor()

    cursor.execute(insert_sql, values)
    connection.commit()

    print("API response saved successfully.")
