from dataclasses import dataclass

from ftrs_common.logger import Logger
from mypy_boto3_dynamodb import DynamoDBClient
from sqlalchemy.engine import Engine

from common.cache import DoSMetadataCache
from service_migration.config import ServiceMigrationConfig


@dataclass
class ServiceMigrationDependencies:
    config: ServiceMigrationConfig
    logger: Logger
    engine: Engine
    ddb_client: DynamoDBClient
    metadata: DoSMetadataCache
