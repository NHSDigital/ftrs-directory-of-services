from decimal import Decimal

import pytest
from botocore.exceptions import ClientError
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain.legacy.data_models import ServiceData
from ftrs_data_layer.domain.legacy.db_models import Service
from pytest_mock import MockerFixture

from service_migration.dependencies import ServiceMigrationDependencies
from service_migration.exceptions import (
    FatalValidationException,
    ServiceMigrationException,
)
from service_migration.processor import (
    ServiceMigrationProcessor,
)
from service_migration.transformer.gp_practice import GPPracticeTransformer
from service_migration.validation.types import ValidationIssue


def test_processor_init(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    processor = ServiceMigrationProcessor(mock_dependencies)

    assert processor.deps == mock_dependencies
    assert processor.metrics.model_dump() == {
        "errored": 0,
        "skipped": 0,
        "inserted": 0,
        "updated": 0,
        "supported": 0,
        "total": 0,
        "transformed": 0,
        "unsupported": 0,
        "invalid": 0,
    }


def test_sync_service_no_existing_state(
    mock_logger: MockLogger,
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    method = "insert"

    assert processor.sync_service(service_id, method) is None

    assert mock_logger.was_logged("SM_PROC_028") is True

    # GP Practice transformer selected
    assert mock_logger.get_log("SM_PROC_005") == [
        {
            "msg": "Transformer GPPracticeTransformer selected for service",
            "detail": {"transformer_name": "GPPracticeTransformer"},
        }
    ]

    # Record validated
    assert mock_logger.get_log("SM_VAL_001") == [
        {
            "msg": "Starting validation of service data using GPPracticeValidator",
            "detail": {"validator_name": "GPPracticeValidator"},
        }
    ]

    # Field changes logged
    assert mock_logger.get_log("SM_VAL_003") == [
        {
            "msg": "Some fields were changed before transformation",
            "detail": {
                "changes": [
                    'Value of root[\'publicphone\'] changed from "01234 567890" to "01234567890".',
                    'Value of root[\'nonpublicphone\'] changed from "09876 543210" to "09876543210".',
                ],
                "validator_name": "GPPracticeValidator",
            },
        }
    ]

    # No existing state
    assert mock_logger.was_logged("SM_PROC_009") is True
    assert mock_logger.was_logged("SM_PROC_010") is False

    assert mock_logger.get_log("SM_PROC_012") == [
        {
            "detail": {"organisation_id": "4539600c-e04e-5b35-a582-9fb36858d0e0"},
            "msg": "Added organisation with ID 4539600c-e04e-5b35-a582-9fb36858d0e0 to migration items",
        }
    ]
    assert mock_logger.get_log("SM_PROC_014") == [
        {
            "detail": {"location_id": "6ef3317e-c6dc-5e27-b36d-577c375eb060"},
            "msg": "Added location with ID 6ef3317e-c6dc-5e27-b36d-577c375eb060 to migration items",
        }
    ]
    assert mock_logger.get_log("SM_PROC_016") == [
        {
            "detail": {"healthcare_service_id": "903cd48b-5d0f-532f-94f4-937a4517b14d"},
            "msg": "Added healthcare service with ID 903cd48b-5d0f-532f-94f4-937a4517b14d to migration items",
        }
    ]
    assert mock_logger.get_log("SM_PROC_023") == [
        {
            "detail": {"source_record_id": "services#1"},
            "msg": "Added migration state insert with source record ID services#1 to migration items",
        }
    ]

    # Verify metrics are updated correctly
    assert processor.metrics.model_dump() == {
        "errored": 0,
        "skipped": 0,
        "inserted": 1,
        "updated": 0,
        "supported": 1,
        "total": 1,
        "transformed": 1,
        "unsupported": 0,
        "invalid": 0,
    }


def test_sync_service_existing_state_no_change(
    mock_logger: MockLogger,
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    method = "update"

    # Run service migration once and check for success
    assert processor.sync_service(service_id, method) is None
    assert mock_logger.was_logged("SM_PROC_028") is True

    mock_logger.clear_logs()

    # Run subsequent service migration with no changes
    assert processor.sync_service(service_id, method) is None

    # Existing state found
    assert mock_logger.was_logged("SM_PROC_009") is False
    assert mock_logger.get_log("SM_PROC_010") == [
        {
            "msg": "Existing state found for service - proceeding with incremental migration",
            "detail": {
                "healthcare_service_id": "903cd48b-5d0f-532f-94f4-937a4517b14d",
                "location_id": "6ef3317e-c6dc-5e27-b36d-577c375eb060",
                "organisation_id": "4539600c-e04e-5b35-a582-9fb36858d0e0",
                "state_version": 1,
            },
        }
    ]

    # No changes detected
    assert mock_logger.was_logged("SM_PROC_017") is True  # No org update
    assert mock_logger.was_logged("SM_PROC_019") is True  # No location update
    assert mock_logger.was_logged("SM_PROC_021") is True  # No healthcare service update

    # No DynamoDB Update
    assert mock_logger.get_log("SM_PROC_026") == [
        {
            "msg": "Skipping DynamoDB transaction as no items to write",
        }
    ]

    # Verify metrics are updated correctly (after two sync_service calls)
    assert processor.metrics.model_dump() == {
        "errored": 0,
        "skipped": 0,
        "inserted": 1,
        "updated": 1,
        "supported": 2,
        "total": 2,
        "transformed": 2,
        "unsupported": 0,
        "invalid": 0,
    }


def test_sync_service_existing_state_org_change(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
    stub_test_services: dict[int, ServiceData],
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    method = "update"

    # Run service migration once and check for success
    assert processor.sync_service(service_id, method) is None
    assert mock_logger.was_logged("SM_PROC_028") is True

    mock_logger.clear_logs()

    # Update the public name to simulate a change in organisation data
    stub_test_services[service_id].publicname = "Updated Public Test Service"

    # Run subsequent service migration with change to the public name
    assert processor.sync_service(service_id, method) is None

    # Existing state found
    assert mock_logger.was_logged("SM_PROC_009") is False
    assert mock_logger.get_log("SM_PROC_010") == [
        {
            "msg": "Existing state found for service - proceeding with incremental migration",
            "detail": {
                "healthcare_service_id": "903cd48b-5d0f-532f-94f4-937a4517b14d",
                "location_id": "6ef3317e-c6dc-5e27-b36d-577c375eb060",
                "organisation_id": "4539600c-e04e-5b35-a582-9fb36858d0e0",
                "state_version": 1,
            },
        }
    ]

    # Organisation changes detected
    assert mock_logger.was_logged("SM_PROC_017") is False
    assert mock_logger.get_log("SM_PROC_018") == [
        {
            "msg": "Organisation changes detected - adding update to migration items",
            "detail": {
                "changes": [
                    'Value of root[\'name\'] changed from "Public Test Service 1" to "Updated Public Test Service".',
                ],
                "diff": {
                    "values_changed": {
                        "root['name']": {
                            "new_value": "Updated Public Test Service",
                            "old_value": "Public Test Service 1",
                        }
                    }
                },
            },
        }
    ]

    assert mock_logger.was_logged("SM_PROC_019") is True  # No location update
    assert mock_logger.was_logged("SM_PROC_021") is True  # No healthcare service update

    # No DynamoDB Update - TODO in next ticket
    assert mock_logger.get_log("SM_PROC_026") == [
        {"msg": "Skipping DynamoDB transaction as no items to write"}
    ]

    # Verify metrics are updated correctly (after two sync_service calls)
    assert processor.metrics.model_dump() == {
        "errored": 0,
        "skipped": 0,
        "inserted": 1,
        "updated": 1,
        "supported": 2,
        "total": 2,
        "transformed": 2,
        "unsupported": 0,
        "invalid": 0,
    }


def test_sync_service_existing_state_location_change(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
    stub_test_services: dict[int, ServiceData],
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    method = "update"

    # Run service migration once and check for success
    assert processor.sync_service(service_id, method) is None
    assert mock_logger.was_logged("SM_PROC_028") is True

    mock_logger.clear_logs()

    # Update the coordinates to trigger location change
    stub_test_services[service_id].latitude = Decimal("52.0000")
    stub_test_services[service_id].longitude = Decimal("-1.0000")

    # Run subsequent service migration with change to the public name
    assert processor.sync_service(service_id, method) is None

    # Existing state found
    assert mock_logger.was_logged("SM_PROC_009") is False
    assert mock_logger.get_log("SM_PROC_010") == [
        {
            "msg": "Existing state found for service - proceeding with incremental migration",
            "detail": {
                "healthcare_service_id": "903cd48b-5d0f-532f-94f4-937a4517b14d",
                "location_id": "6ef3317e-c6dc-5e27-b36d-577c375eb060",
                "organisation_id": "4539600c-e04e-5b35-a582-9fb36858d0e0",
                "state_version": 1,
            },
        }
    ]

    assert mock_logger.was_logged("SM_PROC_017") is True  # No org update
    assert mock_logger.was_logged("SM_PROC_019") is False  # Location update
    assert mock_logger.was_logged("SM_PROC_021") is True  # No healthcare service update

    assert mock_logger.get_log("SM_PROC_020") == [
        {
            "msg": "Location changes detected - adding update to migration items",
            "detail": {
                "changes": [
                    "Value of root['positionGCS']['latitude'] changed from 51.5074 to 52.0000.",
                    "Value of root['positionGCS']['longitude'] changed from -0.1278 to -1.0000.",
                ],
                "diff": {
                    "values_changed": {
                        "root['positionGCS']['latitude']": {
                            "new_value": "52.0000",
                            "old_value": "51.5074",
                        },
                        "root['positionGCS']['longitude']": {
                            "new_value": "-1.0000",
                            "old_value": "-0.1278",
                        },
                    },
                },
            },
        }
    ]

    # No DynamoDB Update - TODO in next ticket
    assert mock_logger.get_log("SM_PROC_026") == [
        {
            "msg": "Skipping DynamoDB transaction as no items to write",
        }
    ]

    # Verify metrics are updated correctly (after two sync_service calls)
    assert processor.metrics.model_dump() == {
        "errored": 0,
        "skipped": 0,
        "inserted": 1,
        "updated": 1,
        "supported": 2,
        "total": 2,
        "transformed": 2,
        "unsupported": 0,
        "invalid": 0,
    }


def test_sync_service_existing_state_healthcare_service_change(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
    stub_test_services: dict[int, ServiceData],
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    method = "update"

    # Run service migration once and check for success
    assert processor.sync_service(service_id, method) is None
    assert mock_logger.was_logged("SM_PROC_028") is True

    mock_logger.clear_logs()

    # Update the telecom details to trigger healthcare service change
    stub_test_services[service_id].publicphone = "01432 999999"
    stub_test_services[service_id].nonpublicphone = None

    # Run subsequent service migration with change to the public name
    assert processor.sync_service(service_id, method) is None

    # Existing state found
    assert mock_logger.was_logged("SM_PROC_009") is False
    assert mock_logger.get_log("SM_PROC_010") == [
        {
            "msg": "Existing state found for service - proceeding with incremental migration",
            "detail": {
                "healthcare_service_id": "903cd48b-5d0f-532f-94f4-937a4517b14d",
                "location_id": "6ef3317e-c6dc-5e27-b36d-577c375eb060",
                "organisation_id": "4539600c-e04e-5b35-a582-9fb36858d0e0",
                "state_version": 1,
            },
        }
    ]

    assert mock_logger.was_logged("SM_PROC_017") is True  # No org update
    assert mock_logger.was_logged("SM_PROC_019") is True  # No location update
    assert mock_logger.was_logged("SM_PROC_021") is False  # Healthcare service update

    assert mock_logger.get_log("SM_PROC_022") == [
        {
            "msg": "Healthcare service changes detected - adding update to migration items",
            "detail": {
                "changes": [
                    "Type of root['telecom']['phone_private'] changed from str to NoneType and value changed from \"09876543210\" to None.",
                    "Value of root['telecom']['phone_public'] changed from \"01234567890\" to \"01432999999\".",
                ],
                "diff": {
                    "type_changes": {
                        "root['telecom']['phone_private']": {
                            "new_type": "<class 'NoneType'>",
                            "new_value": None,
                            "old_type": "<class 'str'>",
                            "old_value": "09876543210",
                        },
                    },
                    "values_changed": {
                        "root['telecom']['phone_public']": {
                            "new_value": "01432999999",
                            "old_value": "01234567890",
                        },
                    },
                },
            },
        }
    ]

    # No DynamoDB Update - TODO in next ticket
    assert mock_logger.get_log("SM_PROC_026") == [
        {"msg": "Skipping DynamoDB transaction as no items to write"}
    ]

    # Verify metrics are updated correctly (after two sync_service calls)
    assert processor.metrics.model_dump() == {
        "errored": 0,
        "skipped": 0,
        "inserted": 1,
        "updated": 1,
        "supported": 2,
        "total": 2,
        "transformed": 2,
        "unsupported": 0,
        "invalid": 0,
    }


def test_get_source_service(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
    stub_test_services: dict[int, Service],
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    service = processor.get_source_service(service_id)

    assert service == ServiceData.model_validate(stub_test_services[service_id])

    assert mock_logger.get_log("SM_PROC_001", level="DEBUG") == [
        {
            "msg": "Querying legacy service data",
            "detail": {
                "statement": (
                    "SELECT pathwaysdos.services.id, pathwaysdos.services.uid, "
                    "pathwaysdos.services.name, pathwaysdos.services.odscode, "
                    "pathwaysdos.services.isnational, "
                    "pathwaysdos.services.openallhours, "
                    "pathwaysdos.services.publicreferralinstructions, "
                    "pathwaysdos.services.telephonetriagereferralinstructions, "
                    "pathwaysdos.services.restricttoreferrals, "
                    "pathwaysdos.services.address, pathwaysdos.services.town, "
                    "pathwaysdos.services.postcode, pathwaysdos.services.easting, "
                    "pathwaysdos.services.northing, pathwaysdos.services.publicphone, "
                    "pathwaysdos.services.nonpublicphone, pathwaysdos.services.fax, "
                    "pathwaysdos.services.email, pathwaysdos.services.web, "
                    "pathwaysdos.services.createdby, pathwaysdos.services.createdtime, "
                    "pathwaysdos.services.modifiedby, "
                    "pathwaysdos.services.modifiedtime, "
                    "pathwaysdos.services.lasttemplatename, "
                    "pathwaysdos.services.lasttemplateid, pathwaysdos.services.typeid, "
                    "pathwaysdos.services.parentid, pathwaysdos.services.subregionid, "
                    "pathwaysdos.services.statusid, "
                    "pathwaysdos.services.organisationid, "
                    "pathwaysdos.services.returnifopenminutes, "
                    "pathwaysdos.services.publicname, pathwaysdos.services.latitude, "
                    "pathwaysdos.services.longitude, "
                    "pathwaysdos.services.professionalreferralinfo, "
                    "pathwaysdos.services.lastverified, "
                    "pathwaysdos.services.nextverificationdue, serviceendpoints_1.id "
                    "AS id_1, serviceendpoints_1.endpointorder, "
                    "serviceendpoints_1.transport, serviceendpoints_1.format, "
                    "serviceendpoints_1.interaction, "
                    "serviceendpoints_1.businessscenario, serviceendpoints_1.address "
                    "AS address_1, serviceendpoints_1.comment, "
                    "serviceendpoints_1.iscompressionenabled, "
                    "serviceendpoints_1.serviceid, servicedayopeningtimes_1.id AS "
                    "id_2, servicedayopeningtimes_1.starttime, "
                    "servicedayopeningtimes_1.endtime, "
                    "servicedayopeningtimes_1.servicedayopeningid, "
                    "servicedayopenings_1.id AS id_3, servicedayopenings_1.serviceid "
                    "AS serviceid_1, servicedayopenings_1.dayid, "
                    "servicespecifiedopeningtimes_1.id AS id_4, "
                    "servicespecifiedopeningtimes_1.starttime AS starttime_1, "
                    "servicespecifiedopeningtimes_1.endtime AS endtime_1, "
                    "servicespecifiedopeningtimes_1.isclosed, "
                    "servicespecifiedopeningtimes_1.servicespecifiedopeningdateid, "
                    "servicespecifiedopeningdates_1.id AS id_5, "
                    "servicespecifiedopeningdates_1.serviceid AS serviceid_2, "
                    "servicespecifiedopeningdates_1.date, servicesgsds_1.id AS id_6, "
                    "servicesgsds_1.serviceid AS serviceid_3, servicesgsds_1.sdid, "
                    "servicesgsds_1.sgid, dispositions_1.id AS id_7, "
                    "dispositions_1.name AS name_1, dispositions_1.dxcode, "
                    "dispositions_1.dispositiontime, servicedispositions_1.id AS id_8, "
                    "servicedispositions_1.serviceid AS serviceid_4, "
                    "servicedispositions_1.dispositionid, serviceagerange_1.id AS "
                    "id_9, serviceagerange_1.serviceid AS serviceid_5, "
                    "serviceagerange_1.daysfrom, serviceagerange_1.daysto \n"
                    "FROM pathwaysdos.services LEFT OUTER JOIN "
                    "pathwaysdos.serviceendpoints AS serviceendpoints_1 ON "
                    "pathwaysdos.services.id = serviceendpoints_1.serviceid LEFT OUTER "
                    "JOIN pathwaysdos.servicedayopenings AS servicedayopenings_1 ON "
                    "pathwaysdos.services.id = servicedayopenings_1.serviceid LEFT "
                    "OUTER JOIN pathwaysdos.servicedayopeningtimes AS "
                    "servicedayopeningtimes_1 ON servicedayopenings_1.id = "
                    "servicedayopeningtimes_1.servicedayopeningid LEFT OUTER JOIN "
                    "pathwaysdos.servicespecifiedopeningdates AS "
                    "servicespecifiedopeningdates_1 ON pathwaysdos.services.id = "
                    "servicespecifiedopeningdates_1.serviceid LEFT OUTER JOIN "
                    "pathwaysdos.servicespecifiedopeningtimes AS "
                    "servicespecifiedopeningtimes_1 ON "
                    "servicespecifiedopeningdates_1.id = "
                    "servicespecifiedopeningtimes_1.servicespecifiedopeningdateid LEFT "
                    "OUTER JOIN pathwaysdos.servicesgsds AS servicesgsds_1 ON "
                    "pathwaysdos.services.id = servicesgsds_1.serviceid LEFT OUTER "
                    "JOIN pathwaysdos.servicedispositions AS servicedispositions_1 ON "
                    "pathwaysdos.services.id = servicedispositions_1.serviceid LEFT "
                    "OUTER JOIN pathwaysdos.dispositions AS dispositions_1 ON "
                    "dispositions_1.id = servicedispositions_1.dispositionid LEFT "
                    "OUTER JOIN pathwaysdos.serviceagerange AS serviceagerange_1 ON "
                    "pathwaysdos.services.id = serviceagerange_1.serviceid \n"
                    "WHERE pathwaysdos.services.id = ?"
                )
            },
        }
    ]

    assert mock_logger.get_log("SM_PROC_002", level="INFO") == [
        {
            "msg": "Legacy service data retrieved",
            "detail": {
                "service_name": "Test Service 1",
                "service_uid": "2000000001",
                "last_updated": "2023-01-02T00:00:00",
            },
        }
    ]


def test_get_source_service_not_found(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    record_id = 9999

    with pytest.raises(
        ServiceMigrationException,
        match="Service record with ID 9999 not found in source database",
    ) as exc_info:
        processor.get_source_service(record_id)

    # Should not requeue as record does not exist
    assert exc_info.value.should_requeue is False


def test_transform_service(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
    stub_test_services: dict[int, ServiceData],
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    data = ServiceData.model_validate(stub_test_services[service_id])

    transformed_items = processor.transform_service(data)

    assert transformed_items.organisation is not None
    assert transformed_items.organisation.name == "Public Test Service 1"

    assert transformed_items.location is not None
    assert transformed_items.location.address.postcode == "AB12 3CD"

    assert transformed_items.healthcare_service is not None
    assert transformed_items.healthcare_service.telecom.phone_public == "01234567890"

    assert transformed_items.validation_issues is not None
    assert transformed_items.validation_issues == []

    assert mock_logger.was_logged("SM_PROC_007") is True
    assert mock_logger.get_log("SM_PROC_007a", level="DEBUG") == [
        {
            "msg": "Service successfully transformed with content",
            "detail": {
                "transformed_record": transformed_items.model_dump(
                    exclude_none=True, mode="json"
                ),
                "original_record": data.model_dump(exclude_none=True, mode="json"),
            },
        }
    ]

    # Verify metrics are updated correctly for transform_service
    assert processor.metrics.model_dump() == {
        "errored": 0,
        "skipped": 0,
        "inserted": 0,
        "updated": 0,
        "supported": 1,
        "total": 0,
        "transformed": 1,
        "unsupported": 0,
        "invalid": 0,
    }


def test_transform_service_should_not_include(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
    stub_test_services: dict[int, ServiceData],
) -> None:
    service_id = 1

    # Make service inactive (not eligible)
    stub_test_services[service_id].statusid = 2  # Inactive status

    processor = ServiceMigrationProcessor(deps=mock_dependencies)
    data = ServiceData.model_validate(stub_test_services[service_id])

    with pytest.raises(
        ServiceMigrationException,
        match="Service skipped during migration: Service is not active",
    ) as exc_info:
        processor.transform_service(data)

    # Should not requeue as service is ineligible
    assert exc_info.value.should_requeue is False

    # Details logged
    assert mock_logger.get_log("SM_PROC_006") == [
        {
            "msg": "Service skipped migration due to reason: Service is not active",
            "detail": {"reason": "Service is not active"},
        }
    ]

    # Verify metrics - supported is incremented before should_include check,
    # but transformed is not incremented since the service was skipped
    assert processor.metrics.model_dump() == {
        "errored": 0,
        "skipped": 0,
        "inserted": 0,
        "updated": 0,
        "supported": 1,
        "total": 0,
        "transformed": 0,
        "unsupported": 0,
        "invalid": 0,
    }


def test_transform_service_fatal_validation_errors(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
    stub_test_services: dict[int, ServiceData],
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    # Introduce fatal validation issue for GPs by removing public name
    service_id = 1
    stub_test_services[service_id].publicname = None
    data = ServiceData.model_validate(stub_test_services[service_id])

    with pytest.raises(
        FatalValidationException,
        match="Fatal validation error for service 1",
    ) as exc_info:
        processor.transform_service(data)

    # Should not requeue as data is invalid
    assert exc_info.value.should_requeue is False
    assert exc_info.value.issues == [
        ValidationIssue(
            value=None,
            severity="fatal",
            code="publicname_required",
            diagnostics="Public name is required for GP practices",
            expression=["publicname"],
        )
    ]

    # Details logged
    assert mock_logger.get_log("SM_VAL_002") == [
        {
            "msg": "Service validation issue identified",
            "detail": {
                "code": "publicname_required",
                "diagnostics": "Public name is required for GP practices",
                "expression": ["publicname"],
                "severity": "fatal",
                "value": None,
            },
        }
    ]

    # Verify metrics - supported is incremented before validation,
    # but transformed is not incremented since validation failed
    assert processor.metrics.model_dump() == {
        "errored": 0,
        "skipped": 0,
        "inserted": 0,
        "updated": 0,
        "supported": 1,
        "total": 0,
        "transformed": 0,
        "unsupported": 0,
        "invalid": 0,
    }


def test_get_transformer_supported_service(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
    stub_test_services: dict[int, ServiceData],
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    data = ServiceData.model_validate(stub_test_services[service_id])

    transformer = processor.get_transformer(data)

    assert transformer.__class__.__name__ == "GPPracticeTransformer"

    assert mock_logger.get_log("SM_PROC_004", level="DEBUG") == [
        {
            "msg": "Transformer GPPracticeTransformer is valid for service",
            "detail": {"transformer_name": "GPPracticeTransformer"},
        }
    ]
    assert mock_logger.get_log("SM_PROC_005", level="INFO") == [
        {
            "msg": "Transformer GPPracticeTransformer selected for service",
            "detail": {"transformer_name": "GPPracticeTransformer"},
        }
    ]


def test_get_transformer_unsupported_service(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
    stub_test_services: dict[int, ServiceData],
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    expected_transformer_checks = 2

    # Set unsupported typeid
    stub_test_services[service_id].typeid = 1000
    data = ServiceData.model_validate(stub_test_services[service_id])

    with pytest.raises(
        ServiceMigrationException,
        match="No suitable transformer found for service ID 1",
    ) as exc_info:
        processor.get_transformer(data)

    # Should not requeue as service is unsupported
    assert exc_info.value.should_requeue is False

    # Should have checked 2 transformers
    assert (
        len(mock_logger.get_log("SM_PROC_003", level="DEBUG"))
        == expected_transformer_checks
    )


def test_get_transformer_multiple_suitable_transformers(
    mock_dependencies: ServiceMigrationDependencies,
    mocker: MockerFixture,
    stub_test_services: dict[int, ServiceData],
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    data = ServiceData.model_validate(stub_test_services[service_id])

    mocker.patch(
        "service_migration.processor.SUPPORTED_TRANSFORMERS",
        [GPPracticeTransformer, GPPracticeTransformer],
    )
    with pytest.raises(
        ServiceMigrationException,
        match="Multiple suitable transformers found for service ID 1: \['GPPracticeTransformer', 'GPPracticeTransformer'\]",
    ) as exc_info:
        processor.get_transformer(data)

    # Should not requeue as service is unsupported
    assert exc_info.value.should_requeue is False


def test_get_state_record_no_existing_record(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    service_id = 1
    assert processor.get_state_record(service_id) is None

    assert mock_logger.get_log("SM_PROC_008", level="DEBUG") == [
        {
            "msg": "Retrieving existing state from DynamoDB",
            "detail": {
                "table_name": "ftrs-dos-local-data-migration-state-table-test-workspace",
                "key": {"source_record_id": {"S": "services#1"}},
            },
        }
    ]
    assert mock_logger.was_logged("SM_PROC_009") is True


def test_get_state_record_existing_record(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    service_id = 1

    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    # Run migration once to create state record
    processor.sync_service(service_id, method="insert")
    mock_logger.clear_logs()

    state_record = processor.get_state_record(service_id)

    assert state_record is not None
    assert state_record.source_record_id == f"services#{service_id}"
    assert state_record.version == 1
    assert str(state_record.organisation_id) == "4539600c-e04e-5b35-a582-9fb36858d0e0"
    assert str(state_record.location_id) == "6ef3317e-c6dc-5e27-b36d-577c375eb060"
    assert (
        str(state_record.healthcare_service_id)
        == "903cd48b-5d0f-532f-94f4-937a4517b14d"
    )

    assert mock_logger.get_log("SM_PROC_008", level="DEBUG") == [
        {
            "msg": "Retrieving existing state from DynamoDB",
            "detail": {
                "table_name": "ftrs-dos-local-data-migration-state-table-test-workspace",
                "key": {"source_record_id": {"S": "services#1"}},
            },
        }
    ]
    assert mock_logger.was_logged("SM_PROC_009") is False

    assert mock_logger.get_log("SM_PROC_010") == [
        {
            "msg": "Existing state found for service - proceeding with incremental migration",
            "detail": {
                "healthcare_service_id": "903cd48b-5d0f-532f-94f4-937a4517b14d",
                "location_id": "6ef3317e-c6dc-5e27-b36d-577c375eb060",
                "organisation_id": "4539600c-e04e-5b35-a582-9fb36858d0e0",
                "state_version": 1,
            },
        }
    ]


def test_execute_transaction(
    mocker: MockerFixture,
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    processor = ServiceMigrationProcessor(deps=mock_dependencies)
    processor.deps.ddb_client = mocker.MagicMock()
    processor.deps.ddb_client.transact_write_items = mocker.MagicMock(
        return_value={"ConsumedCapacity": []}
    )

    transact_items = [
        {"Put": {"TableName": "TestTable", "Item": {"id": {"S": "1"}}}},
        {"Put": {"TableName": "TestTable", "Item": {"id": {"S": "2"}}}},
    ]

    assert processor.execute_transaction(transact_items) is None

    assert mock_logger.get_log("SM_PROC_027", level="DEBUG") == [
        {
            "msg": "Executing DynamoDB transaction with 2 items",
            "detail": {"items": transact_items, "item_count": 2},
        }
    ]

    processor.deps.ddb_client.transact_write_items.assert_called_once_with(
        TransactItems=transact_items,
        ReturnConsumedCapacity="INDEXES",
    )

    assert mock_logger.get_log("SM_PROC_028") == [
        {
            "msg": "DynamoDB transaction completed successfully",
            "detail": {"consumed_capacity": []},
        }
    ]


def test_execute_transaction_handles_conditional_check_failed(
    mocker: MockerFixture,
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that execute_transaction handles TransactionCanceledException with ConditionalCheckFailed gracefully."""
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    processor.deps.ddb_client = mocker.MagicMock()

    # Mock DynamoDB client to raise the exception
    processor.deps.ddb_client.transact_write_items.side_effect = ClientError(
        error_response={
            "Error": {
                "Code": "TransactionCanceledException",
                "Message": "Transaction cancelled",
            },
            "CancellationReasons": [
                {"Code": "ConditionalCheckFailed"},
                {"Code": "ConditionalCheckFailed"},
                {"Code": "None"},
                {"Code": "ConditionalCheckFailed"},
            ],
        },
        operation_name="TransactWriteItems",
    )

    transact_items = [
        {"Put": {"TableName": "TestTable", "Item": {"id": {"S": "1"}}}},
        {"Put": {"TableName": "TestTable", "Item": {"id": {"S": "2"}}}},
        {"Update": {"TableName": "TestTable", "Key": {"id": {"S": "3"}}}},
        {"Delete": {"TableName": "TestTable", "Key": {"id": {"S": "4"}}}},
    ]

    with pytest.raises(
        ServiceMigrationException,
        match="DynamoDB transaction cancelled: see logs for details",
    ) as exc_info:
        processor.execute_transaction(transact_items)

    # Should requeue as this should be a transient issue
    assert exc_info.value.should_requeue is True

    assert mock_logger.get_log("SM_PROC_029") == [
        {
            "msg": "DynamoDB transaction cancelled due to conditional check failure: Transaction cancelled",
            "detail": {
                "error": "Transaction cancelled",
                "items": transact_items,
                "response": {
                    "CancellationReasons": [
                        {"Code": "ConditionalCheckFailed"},
                        {"Code": "ConditionalCheckFailed"},
                        {"Code": "None"},
                        {"Code": "ConditionalCheckFailed"},
                    ],
                    "Error": {
                        "Code": "TransactionCanceledException",
                        "Message": "Transaction cancelled",
                    },
                },
            },
        }
    ]
    assert mock_logger.was_logged("SM_PROC_030") is False


def test_execute_transaction_handles_other_client_error(
    mocker: MockerFixture,
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that execute_transaction handles other ClientError exceptions correctly."""
    processor = ServiceMigrationProcessor(deps=mock_dependencies)

    processor.deps.ddb_client = mocker.MagicMock()

    # Mock DynamoDB client to raise a generic ClientError
    processor.deps.ddb_client.transact_write_items.side_effect = ClientError(
        error_response={
            "Error": {
                "Code": "ProvisionedThroughputExceededException",
                "Message": "Throughput exceeded",
            }
        },
        operation_name="TransactWriteItems",
    )

    transact_items = [
        {"Put": {"TableName": "TestTable", "Item": {"id": {"S": "1"}}}},
        {"Put": {"TableName": "TestTable", "Item": {"id": {"S": "2"}}}},
    ]

    with pytest.raises(
        ServiceMigrationException,
        match="DynamoDB transaction failed: Throughput exceeded",
    ) as exc_info:
        processor.execute_transaction(transact_items)

    # Should requeue as this should be a transient issue
    assert exc_info.value.should_requeue is True

    assert mock_logger.get_log("SM_PROC_030") == [
        {
            "msg": "DynamoDB transaction failed: Throughput exceeded",
            "detail": {
                "error": "Throughput exceeded",
                "items": transact_items,
                "response": {
                    "Error": {
                        "Code": "ProvisionedThroughputExceededException",
                        "Message": "Throughput exceeded",
                    }
                },
            },
        }
    ]
