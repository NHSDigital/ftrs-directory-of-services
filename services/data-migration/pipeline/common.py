from functools import lru_cache

from sqlalchemy import Engine, create_engine

# TODO for FDOS-183:
# 2) use AWS Lambda powertools to retrieve details of source database from secrets manager


@lru_cache
def get_db_engine(connection_uri: str) -> Engine:
    return create_engine(connection_uri)
