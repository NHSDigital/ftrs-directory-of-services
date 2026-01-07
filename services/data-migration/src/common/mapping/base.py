from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar

from ftrs_data_layer.domain import DBModel
from ftrs_data_layer.domain.legacy.data_models import LegacyDoSDataModel

from service_migration.dependencies import ServiceMigrationDependencies

LegacyDoSModelType = TypeVar("LegacyDoSModelType", bound=LegacyDoSDataModel)
FutureDoSModelType = TypeVar("FutureDoSModelType", bound=DBModel)


class BaseMapper(Generic[LegacyDoSModelType, FutureDoSModelType], ABC):
    def __init__(
        self,
        deps: ServiceMigrationDependencies,
        start_time: datetime,
    ) -> None:
        self.metadata = deps.metadata
        self.logger = deps.logger
        self.start_time = start_time

    @abstractmethod
    def map(self, source: LegacyDoSModelType) -> FutureDoSModelType:
        raise NotImplementedError
