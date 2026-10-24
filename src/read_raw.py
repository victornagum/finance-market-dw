import json

from config import db_connection


def read_raw_response(api_response_id=None):
    """Return (ApiResponseID, parsed_json).

    Pass an explicit ID to process a specific batch; with no ID the latest
    row is used (handy for manual runs).
    """
    with db_connection() as connection:
        cursor = connection.cursor()
        if api_response_id is None:
            cursor.execute(
                "SELECT TOP 1 ApiResponseID, ResponseJson "
                "FROM raw.ApiResponse ORDER BY ApiResponseID DESC;"
            )
        else:
            cursor.execute(
                "SELECT ApiResponseID, ResponseJson "
                "FROM raw.ApiResponse WHERE ApiResponseID = ?;",
                api_response_id,
            )
        row = cursor.fetchone()

    # FIX: previously `data` was undefined (NameError) on an empty table.
    if row is None:
        raise LookupError("No matching row found in raw.ApiResponse.")

    return row[0], json.loads(row[1])
