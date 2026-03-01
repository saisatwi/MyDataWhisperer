import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="Sana_db",
        user="postgres",
        password="Postgres@1319",
        port="5432"
    )
