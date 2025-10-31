from sqlalchemy import Engine, create_engine

from common.config import DatabaseConfig


def get_sqlalchemy_engine_from_config(db_config: DatabaseConfig) -> Engine:
    """Create and configure an SQLAlchemy engine from DatabaseConfig with optimized settings."""
    return create_engine(
        url=db_config.connection_string,
        # Connection pool settings for better performance
        pool_size=10,  # Number of connections to maintain in a pool
        max_overflow=20,  # Additional connections beyond pool_size
        pool_pre_ping=True,  # Validate connections before use
        pool_recycle=3600,  # Recycle connections after 1 hour
        # Connection timeout settings
        connect_args={
            "connect_timeout": 30,  # Connection timeout in seconds
            "application_name": "dms_pipeline",  # Identify your application in pg_stat_activity
        },
        # Enable connection pooling optimizations
        pool_reset_on_return="commit",  # Reset connections on return to pool
    )
