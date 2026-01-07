from datetime import UTC, datetime

import pytest
from freezegun import freeze_time
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain.legacy.data_models import ServiceData

from service_migration.dependencies import ServiceMigrationDependencies
from service_migration.transformer import ServiceTransformer


class BasicServiceTransformer(ServiceTransformer):
    def transform(self, service: ServiceData) -> dict:
        return super().transform(service)

    @classmethod
    def is_service_supported(cls, service: ServiceData) -> tuple[bool, str | None]:
        return super().is_service_supported(service)

    @classmethod
    def should_include_service(cls, service: ServiceData) -> tuple[bool, str | None]:
        return super().should_include_service(service)


@freeze_time("2025-07-17T12:00:00")
def test_service_transformer_init(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    transformer = BasicServiceTransformer(deps=mock_dependencies)

    assert transformer.logger == mock_dependencies.logger
    assert transformer.mappers is not None

    assert transformer.mappers.organisation.metadata == mock_dependencies.metadata
    assert transformer.mappers.location.metadata == mock_dependencies.metadata
    assert transformer.mappers.healthcare_service.metadata == mock_dependencies.metadata

    assert transformer.start_time == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)

    with pytest.raises(NotImplementedError):
        transformer.transform(None)

    assert transformer.is_service_supported(None) == (False, None)
    assert transformer.should_include_service(None) == (False, None)


def test_service_transformer_abstract_methods(mock_logger: MockLogger) -> None:
    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class ServiceTransformer without an implementation for abstract methods 'is_service_supported', 'should_include_service', 'transform'",
    ):
        ServiceTransformer(logger=mock_logger)
