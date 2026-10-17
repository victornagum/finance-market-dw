import json

from config import get_connection
from extract import fetch_market_data

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


with get_connection() as connection:
    cursor = connection.cursor()

    cursor.execute(insert_sql, values)
    connection.commit()

    print("API response saved successfully.")
