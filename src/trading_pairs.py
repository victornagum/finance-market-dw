
from config import db_connection


def get_active_trading_pairs():
    """Retrieve all active trading pairs from the warehouse configuration."""

    query = """
        SELECT PairKey, Symbol
        FROM config.TradingPair
        WHERE IsActive = 1
        ORDER BY PairKey;
    """

    with db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query)

        rows = cursor.fetchall()

    return [
        {
            "pair_key": row[0],
            "symbol": row[1]
        }
        for row in rows
    ]


if __name__ == "__main__":
    pairs = get_active_trading_pairs()

    for pair in pairs:
        print(pair)
