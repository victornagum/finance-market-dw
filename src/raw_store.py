import json

from config import db_connection

INSERT_SQL = """
    INSERT INTO raw.ApiResponse (SourceName, Endpoint, RequestParams, ResponseJson)
    OUTPUT INSERTED.ApiResponseID
    VALUES (?, ?, ?, ?);
"""


def save_raw_response(endpoint, params, data, source_name="Binance"):
    """Persist the untouched API response and return its ApiResponseID.

    Single shared implementation (was duplicated in load_raw.py and
    load_history.py).
    """
    with db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            INSERT_SQL,
            (source_name, endpoint, json.dumps(params), json.dumps(data)),
        )
        return cursor.fetchone()[0]
