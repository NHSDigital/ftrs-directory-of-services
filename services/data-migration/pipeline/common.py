from functools import lru_cache

from sqlalchemy import Engine, create_engine


@lru_cache
def get_db_engine(connection_uri: str) -> Engine:
    return create_engine(connection_uri)
