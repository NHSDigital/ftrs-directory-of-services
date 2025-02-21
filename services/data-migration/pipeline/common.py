import psycopg


def get_db_connection(connection_uri: str) -> psycopg.Connection:
    return psycopg.connect(connection_uri)
