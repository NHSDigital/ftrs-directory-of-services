from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Type
from uuid import UUID

from ftrs_data_layer.domain.legacy.data_models import ServiceData

from common.mapping import HealthcareServiceMapper, LocationMapper, OrganisationMapper
from service_migration.dependencies import ServiceMigrationDependencies
from service_migration.models import TransformResult
from service_migration.validation.base import Validator
from service_migration.validation.service import ServiceValidator


class ServiceMappers:
    """
    Container for the various mappers used in service transformation.
    """

    def __init__(
        self,
        deps: ServiceMigrationDependencies,
        start_time: datetime,
    ) -> None:
        self.organisation = OrganisationMapper(deps, start_time)
        self.location = LocationMapper(deps, start_time)
        self.healthcare_service = HealthcareServiceMapper(deps, start_time)


class ServiceTransformer(ABC):
    """
    Abstract base class for transforming service data.
    """

    MIGRATION_UUID_NS = UUID("fa3aaa15-9f83-4f4a-8f86-fd1315248bcb")
    MIGRATION_USER = "DATA_MIGRATION"
    VALIDATOR_CLS: Type[Validator] = ServiceValidator

    def __init__(self, deps: ServiceMigrationDependencies) -> None:
        self.start_time = datetime.now(UTC)
        self.mappers = ServiceMappers(deps, self.start_time)
        self.validator = self.VALIDATOR_CLS(deps)
        self.logger = deps.logger

    @abstractmethod
    def transform(self, service: ServiceData) -> TransformResult:
        """
        Transform the given service data into a dictionary format.

        :param validation_issues:
        :param service: The service data to transform.
        :return: A dictionary representation of the transformed service data.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    @abstractmethod
    def is_service_supported(cls, service: ServiceData) -> tuple[bool, str | None]:
        """
        Check if the service is supported by this transformer for transformation.

        :param service: The service data to check.
        :return: A tuple (bool, str) indicating if the service is supported and a reason if not.
        """
        return False, None

    @classmethod
    @abstractmethod
    def should_include_service(cls, service: ServiceData) -> tuple[bool, str | None]:
        """
        Check if the service record can be should be included in the transformation.

        :param service: The service data to check.
        :return: A tuple (bool, str) indicating if the record is transformable and a reason if not.
        """
        return False, None
