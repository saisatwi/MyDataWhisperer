import pandas as pd
from db_connection import get_connection

def fetch_features():
    conn = get_connection()
    query = """
    SELECT
        LENGTH(user_query) AS query_length,
        response_time,
        confidence_score
    FROM interactions
    WHERE confidence_score IS NOT NULL;
    """
    return pd.read_sql(query, conn)
