
import json

from config import db_connection


def read_raw_response(api_response_id=None):
    """Return (ApiResponseID, request_params, parsed_json).

    Pass an explicit ID to process a specific batch.
    Otherwise, the latest raw response is used.
    """
    with db_connection() as connection:
        cursor = connection.cursor()

        if api_response_id is None:
            cursor.execute(
                """
                SELECT TOP 1
                    ApiResponseID,
                    RequestParams,
                    ResponseJson
                FROM raw.ApiResponse
                ORDER BY ApiResponseID DESC;
                """
            )
        else:
            cursor.execute(
                """
                SELECT
                    ApiResponseID,
                    RequestParams,
                    ResponseJson
                FROM raw.ApiResponse
                WHERE ApiResponseID = ?;
                """,
                api_response_id
            )

        row = cursor.fetchone()

    if row is None:
        raise LookupError(
            "No matching row found in raw.ApiResponse."
        )

    return (
        row[0],
        json.loads(row[1]),
        json.loads(row[2])
    )
