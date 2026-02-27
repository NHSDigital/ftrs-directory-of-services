from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Type
from uuid import UUID

from ftrs_common.logger import Logger
from ftrs_data_layer.domain import (
    HealthcareService,
    Location,
    Organisation,
)
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from pydantic import BaseModel, Field
from sqlalchemy import Engine

from common.cache import DoSMetadataCache
from service_migration.validation.base import Validator
from service_migration.validation.service import ServiceValidator

if TYPE_CHECKING:
    from service_migration.models import ServiceMigrationState


class ServiceTransformOutput(BaseModel):
    """
    Represents the output of a service transformation.

    This may be adapted in the future to better reflect relationships/data deduplication.
    """

    organisation: list[Organisation] = Field(default_factory=list)
    healthcare_service: list[HealthcareService] = Field(default_factory=list)
    location: list[Location] = Field(default_factory=list)


class ServiceTransformer(ABC):
    """
    Abstract base class for transforming service data.
    """

    MIGRATION_UUID_NS = UUID("fa3aaa15-9f83-4f4a-8f86-fd1315248bcb")
    MIGRATION_USER = AuditEvent(
        type=AuditEventType.app, value="INTERNAL001", display="Data Migration"
    )
    VALIDATOR_CLS: Type[Validator] = ServiceValidator

    def __init__(
        self,
        logger: Logger,
        metadata: DoSMetadataCache,
    ) -> None:
        self.start_time = datetime.now(UTC)
        self.logger = logger
        self.metadata = metadata
        self.validator = self.VALIDATOR_CLS(logger)

    @abstractmethod
    def transform(self, service: legacy_model.Service) -> ServiceTransformOutput:
        """
        Transform the given service data into a dictionary format.

        :param service: The service data to transform.
        :return: A dictionary representation of the transformed service data.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    @abstractmethod
    def is_service_supported(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        """
        Check if the service is supported by this transformer for transformation.

        :param service: The service data to check.
        :return: A tuple (bool, str) indicating if the service is supported and a reason if not.
        """
        return False, None

    @classmethod
    @abstractmethod
    def should_include_service(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        """
        Check if the service record can be should be included in the transformation.

        :param service: The service data to check.
        :return: A tuple (bool, str) indicating if the record is transformable and a reason if not.
        """
        return False, None


class LinkedPharmacyTransformer(ServiceTransformer):
    """
    Abstract base class for transformers that produce a service linked to a separately-migrated
    parent record (e.g. a pharmacy service linked to a parent pharmacy organisation/location).

    Subclasses must implement `resolve_parent` to determine the parent's organisation and
    location IDs before transformation, and set them on the instance prior to `transform()`.
    """

    @abstractmethod
    def resolve_parent(
        self,
        service: legacy_model.Service,
        engine: Engine,
        get_state_record: Callable[[int], "ServiceMigrationState | None"],
    ) -> tuple[legacy_model.Service | None, UUID | None, UUID | None]:
        """
        Resolve the parent record for a linked service.

        :param service: The legacy service being processed.
        :param engine: SQLAlchemy engine for querying the legacy database.
        :param get_state_record: Callable to fetch migration state by legacy service ID.
        :return: Tuple of (parent_legacy_service_or_None, org_id_or_None, loc_id_or_None).
                 If parent state already exists, returns (None, org_id, loc_id).
                 If parent needs migrating, returns (parent_service, None, None).
        """
        ...
