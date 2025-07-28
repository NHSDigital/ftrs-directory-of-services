# from datetime import UTC, date, datetime, time
# from decimal import Decimal

# import pytest
# from freezegun import freeze_time
# from ftrs_common.mocks.mock_logger import MockLogger
# from ftrs_data_layer.domain import (
#     Endpoint,
#     HealthcareService,
#     Location,
#     Organisation,
#     PositionGCS,
# )
# from ftrs_data_layer.domain.legacy import (
#     OpeningTimeDay,
#     Service,
#     ServiceDayOpening,
#     ServiceDayOpeningTime,
#     ServiceEndpoint,
#     ServiceSpecifiedOpeningDate,
#     ServiceSpecifiedOpeningTime,
# )

# from pipeline.transformer.base import ServiceTransformer


# class BasicServiceTransformer(ServiceTransformer):
#     def is_service_supported(self, service: Service) -> tuple[bool, str | None]:
#         return super().is_service_supported(service)

#     def should_include_service(self, service: Service) -> tuple[bool, str | None]:
#         return super().should_include_service(service)

#     def transform(self, service: Service) -> dict:
#         return super().transform(service)


# def test_service_transformer_is_abstract() -> None:
#     """
#     Test that ServiceTransformer is an abstract class and cannot be instantiated directly.
#     """
#     with pytest.raises(
#         TypeError,
#         match="Can't instantiate abstract class ServiceTransformer without an implementation for abstract methods 'is_service_supported', 'should_include_service', 'transform'",
#     ):
#         ServiceTransformer()


# @freeze_time("2025-07-17T12:00:00")
# def test_service_transformer_sets_start_time_and_logger(
#     mock_logger: MockLogger,
# ) -> None:
#     """
#     Test that ServiceTransformer sets start_time and logger correctly.
#     """
#     transformer = BasicServiceTransformer(logger=mock_logger)

#     assert transformer.start_time == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
#     assert transformer.logger == mock_logger

#     with pytest.raises(NotImplementedError):
#         transformer.transform(None)


# def test_service_transformer_is_service_supported() -> None:
#     """
#     Test that is_service_supported method defaults to returning False and None for unsupported services.
#     """
#     transformer = BasicServiceTransformer(logger=MockLogger())
#     result = transformer.is_service_supported(None)

#     assert result == (False, None)


# def test_service_transformer_should_include_service() -> None:
#     """
#     Test that should_include_service method defaults to returning False and None for unsupported services.
#     """
#     transformer = BasicServiceTransformer(logger=MockLogger())
#     result = transformer.should_include_service(None)

#     assert result == (False, None)


# @freeze_time("2025-07-17T12:00:00")
# def test_service_transformer_build_organisation(
#     mock_service: Service,
# ) -> None:
#     """
#     Test that build_organisation method raises NotImplementedError.
#     """
#     transformer = BasicServiceTransformer(logger=MockLogger())

#     result = transformer.build_organisation(mock_service)

#     assert isinstance(result, Organisation)
#     assert result.model_dump(mode="json") == {
#         "active": True,
#         "createdBy": "DATA_MIGRATION",
#         "createdDateTime": "2025-07-17T12:00:00Z",
#         "endpoints": [],
#         "id": "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
#         "identifier_ODS_ODSCode": "A12345",
#         "modifiedBy": "DATA_MIGRATION",
#         "modifiedDateTime": "2025-07-17T12:00:00Z",
#         "name": "Test Service",
#         "telecom": None,
#         "type": "GP Practice",
#     }


# @freeze_time("2025-07-17T12:00:00")
# def test_service_transformer_build_organisation_with_endpoints(
#     mock_service: Service,
# ) -> None:
#     """
#     Test that build_organisation method includes endpoints when provided.
#     """
#     mock_service.endpoints = [
#         ServiceEndpoint(
#             id=12345,
#             endpointorder=1,
#             transport="itk",
#             format="xml",
#             interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
#             businessscenario="Primary",
#             address="http://example.com/endpoint1",
#             comment="Test Endpoint 1",
#             iscompressionenabled="compressed",
#             serviceid=mock_service.id,
#         ),
#         ServiceEndpoint(
#             id=67890,
#             endpointorder=2,
#             transport="telno",
#             format=None,
#             interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
#             businessscenario="Copy",
#             address="tel:01234567890",
#             comment="Test Endpoint 2",
#             iscompressionenabled=None,
#             serviceid=mock_service.id,
#         ),
#     ]

#     transformer = BasicServiceTransformer(logger=MockLogger())

#     result = transformer.build_organisation(mock_service)

#     assert isinstance(result, Organisation)
#     assert len(result.endpoints) == len(mock_service.endpoints)

#     assert result.endpoints[0].model_dump(mode="json") == {
#         "address": "http://example.com/endpoint1",
#         "connectionType": "itk",
#         "createdBy": "DATA_MIGRATION",
#         "createdDateTime": "2025-07-17T12:00:00Z",
#         "description": "Primary",
#         "id": "01d78de8-4e63-53b3-9b7d-107c39c23a8d",
#         "identifier_oldDoS_id": 12345,
#         "isCompressionEnabled": True,
#         "managedByOrganisation": "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
#         "modifiedBy": "DATA_MIGRATION",
#         "modifiedDateTime": "2025-07-17T12:00:00Z",
#         "name": None,
#         "order": 1,
#         "payloadMimeType": "xml",
#         "payloadType": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
#         "service": None,
#         "status": "active",
#     }
#     assert result.endpoints[1].model_dump(mode="json") == {
#         "address": "tel:01234567890",
#         "connectionType": "telno",
#         "createdBy": "DATA_MIGRATION",
#         "createdDateTime": "2025-07-17T12:00:00Z",
#         "description": "Copy",
#         "id": "4f1a685e-15da-5324-b596-6090fc90dc49",
#         "identifier_oldDoS_id": 67890,
#         "isCompressionEnabled": False,
#         "managedByOrganisation": "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
#         "modifiedBy": "DATA_MIGRATION",
#         "modifiedDateTime": "2025-07-17T12:00:00Z",
#         "name": None,
#         "order": 2,
#         "payloadMimeType": None,
#         "payloadType": None,
#         "service": None,
#         "status": "active",
#     }


# @freeze_time("2025-07-17T12:00:00")
# def test_service_transformer_build_endpoint() -> None:
#     """
#     Test that build_endpoint method creates an Endpoint instance from the source DoS endpoint data.
#     """
#     transformer = BasicServiceTransformer(logger=MockLogger())
#     mock_endpoint = ServiceEndpoint(
#         id=12345,
#         endpointorder=1,
#         transport="itk",
#         format="xml",
#         interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
#         businessscenario="Primary",
#         address="http://example.com/endpoint1",
#         comment="Test Endpoint 1",
#         iscompressionenabled="compressed",
#         serviceid=123456,
#     )

#     organisation_id = "0fd917b6-608a-59a0-ba62-eba57ec06a0e"
#     result = transformer.build_endpoint(mock_endpoint, organisation_id)

#     assert isinstance(result, Endpoint)
#     assert result.model_dump(mode="json") == {
#         "address": "http://example.com/endpoint1",
#         "connectionType": "itk",
#         "createdBy": "DATA_MIGRATION",
#         "description": "Primary",
#         "id": "01d78de8-4e63-53b3-9b7d-107c39c23a8d",
#         "identifier_oldDoS_id": 12345,
#         "isCompressionEnabled": True,
#         "managedByOrganisation": "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
#         "modifiedBy": "DATA_MIGRATION",
#         "name": None,
#         "order": 1,
#         "payloadMimeType": "xml",
#         "payloadType": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
#         "service": None,
#         "status": "active",
#         "createdDateTime": "2025-07-17T12:00:00Z",
#         "modifiedDateTime": "2025-07-17T12:00:00Z",
#     }


# @freeze_time("2025-07-17T12:00:00")
# def test_service_transformer_build_endpoint_with_telno() -> None:
#     """
#     Test that build_endpoint method handles 'telno' transport correctly.
#     """
#     transformer = BasicServiceTransformer(logger=MockLogger())
#     mock_endpoint = ServiceEndpoint(
#         id=67890,
#         endpointorder=2,
#         transport="telno",
#         format=None,
#         interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
#         businessscenario="Copy",
#         address="tel:01234567890",
#         comment="Test Endpoint 2",
#         iscompressionenabled=None,
#         serviceid=123456,
#     )

#     organisation_id = "0fd917b6-608a-59a0-ba62-eba57ec06a0e"
#     result = transformer.build_endpoint(mock_endpoint, organisation_id)

#     assert isinstance(result, Endpoint)
#     assert result.model_dump(mode="json") == {
#         "address": "tel:01234567890",
#         "connectionType": "telno",
#         "createdBy": "DATA_MIGRATION",
#         "description": "Copy",
#         "id": "4f1a685e-15da-5324-b596-6090fc90dc49",
#         "identifier_oldDoS_id": 67890,
#         "isCompressionEnabled": False,
#         "managedByOrganisation": "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
#         "modifiedBy": "DATA_MIGRATION",
#         "name": None,
#         "order": 2,
#         "payloadMimeType": None,
#         "payloadType": None,
#         "service": None,
#         "status": "active",
#         "createdDateTime": "2025-07-17T12:00:00Z",
#         "modifiedDateTime": "2025-07-17T12:00:00Z",
#     }


# @freeze_time("2025-07-17T12:00:00")
# def test_service_transformer_build_location(mock_service: Service) -> None:
#     mock_service.latitude = Decimal("51.5074")
#     mock_service.longitude = Decimal("-0.1278")

#     transformer = BasicServiceTransformer(logger=MockLogger())

#     result = transformer.build_location(
#         mock_service, "0fd917b6-608a-59a0-ba62-eba57ec06a0e"
#     )

#     assert isinstance(result, Location)
#     assert result.model_dump(mode="json") == {
#         "active": True,
#         "address": {
#             "postcode": "TE1 2ST",
#             "street": "123 Test St",
#             "town": "Test Town",
#         },
#         "createdBy": "DATA_MIGRATION",
#         "createdDateTime": "2025-07-17T12:00:00Z",
#         "id": "65f34381-acc8-5315-9b81-ff4e4dbef8d2",
#         "managingOrganisation": "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
#         "modifiedBy": "DATA_MIGRATION",
#         "modifiedDateTime": "2025-07-17T12:00:00Z",
#         "name": None,
#         "partOf": None,
#         "positionGCS": {
#             "latitude": "51.5074",
#             "longitude": "-0.1278",
#         },
#         "positionReferenceNumber_UBRN": None,
#         "positionReferenceNumber_UPRN": None,
#         "primaryAddress": True,
#     }


# @pytest.mark.parametrize(
#     "latitude, longitude, expected",
#     [
#         (Decimal("51.5074"), Decimal("-0.1278"), True),
#         (None, None, False),
#         (Decimal("0.0"), Decimal("0.0"), True),
#     ],
# )
# def test_service_transformer_build_location_position(
#     latitude: Decimal, longitude: Decimal, expected: bool
# ) -> None:
#     transformer = BasicServiceTransformer(logger=MockLogger())
#     mock_service = Service()
#     mock_service.latitude = latitude
#     mock_service.longitude = longitude

#     result = transformer.build_location(
#         mock_service, "0fd917b6-608a-59a0-ba62-eba57ec06a0e"
#     )

#     if expected:
#         assert isinstance(result.positionGCS, PositionGCS)
#         assert result.positionGCS.latitude == latitude
#         assert result.positionGCS.longitude == longitude

#     else:
#         assert result.positionGCS is None


# @freeze_time("2025-07-17T12:00:00")
# def test_service_transformer_build_healthcare_service(
#     mock_service: Service,
# ) -> None:
#     """
#     Test that build_healthcare_service method creates a HealthcareService instance from the source DoS service data.
#     """
#     transformer = BasicServiceTransformer(logger=MockLogger())
#     organisation_id = "0fd917b6-608a-59a0-ba62-eba57ec06a0e"
#     location_id = "65f34381-acc8-5315-9b81-ff4e4dbef8d2"

#     result = transformer.build_healthcare_service(
#         mock_service,
#         organisation_id,
#         location_id,
#         category="GP Services",
#         type="GP Consultation Service",
#     )

#     assert isinstance(result, HealthcareService)
#     assert result.model_dump(mode="json") == {
#         "active": True,
#         "category": "GP Services",
#         "createdBy": "DATA_MIGRATION",
#         "createdDateTime": "2025-07-17T12:00:00Z",
#         "id": "39ff9286-3313-5970-ba22-0ab84c58c5ad",
#         "identifier_oldDoS_uid": "1234567890",
#         "location": "65f34381-acc8-5315-9b81-ff4e4dbef8d2",
#         "modifiedBy": "DATA_MIGRATION",
#         "modifiedDateTime": "2025-07-17T12:00:00Z",
#         "name": "Test Service",
#         "openingTime": [],
#         "providedBy": "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
#         "telecom": {
#             "email": "test.service@example.com",
#             "phone_private": None,
#             "phone_public": "01234 567890",
#             "web": "http://example.com",
#         },
#         "type": "GP Consultation Service",
#     }


# @freeze_time("2025-07-17T12:00:00")
# def test_service_transformer_build_healthcare_service_with_opening_times(
#     mock_service: Service,
# ) -> None:
#     """ """
#     transformer = BasicServiceTransformer(logger=MockLogger())

#     mock_service.scheduled_opening_times = [
#         ServiceDayOpening(
#             id=1,
#             dayid=1,
#             day=OpeningTimeDay(id=1, name="Monday"),
#             times=[
#                 ServiceDayOpeningTime(
#                     id=1,
#                     starttime=time(9, 0),
#                     endtime=time(17, 0),
#                     servicedayopeningid=1,
#                 )
#             ],
#         ),
#         ServiceDayOpening(
#             id=2,
#             dayid=3,
#             day=OpeningTimeDay(id=3, name="Tuesday"),
#             times=[
#                 ServiceDayOpeningTime(
#                     id=2,
#                     starttime=time(9, 0),
#                     endtime=time(12, 0),
#                     servicedayopeningid=2,
#                 ),
#                 ServiceDayOpeningTime(
#                     id=2,
#                     starttime=time(13, 0),
#                     endtime=time(17, 0),
#                     servicedayopeningid=2,
#                 ),
#             ],
#         ),
#         ServiceDayOpening(
#             id=3,
#             dayid=5,
#             day=OpeningTimeDay(id=5, name="Friday"),
#             times=[
#                 ServiceDayOpeningTime(
#                     id=5,
#                     starttime=time(9, 0),
#                     endtime=time(17, 0),
#                     servicedayopeningid=3,
#                 )
#             ],
#         ),
#         ServiceDayOpening(
#             id=4,
#             dayid=8,
#             day=OpeningTimeDay(id=8, name="BankHoliday"),
#             times=[
#                 ServiceDayOpeningTime(
#                     id=5,
#                     starttime=time(10, 0),
#                     endtime=time(16, 0),
#                     servicedayopeningid=3,
#                 )
#             ],
#         ),
#     ]
#     mock_service.specified_opening_times = [
#         ServiceSpecifiedOpeningDate(
#             id=1,
#             serviceid=mock_service.id,
#             date=date(2025, 7, 15),
#             times=[
#                 ServiceSpecifiedOpeningTime(
#                     id=1,
#                     isclosed=False,
#                     starttime=time(9, 0),
#                     endtime=time(17, 0),
#                 )
#             ],
#         ),
#         ServiceSpecifiedOpeningDate(
#             id=2,
#             serviceid=mock_service.id,
#             date=date(2025, 7, 16),
#             times=[
#                 ServiceSpecifiedOpeningTime(
#                     id=2,
#                     isclosed=True,
#                     starttime=time(0, 0),
#                     endtime=time(23, 59),
#                 )
#             ],
#         ),
#     ]

#     result = transformer.build_healthcare_service(
#         mock_service,
#         "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
#         "65f34381-acc8-5315-9b81-ff4e4dbef8d2",
#         category="GP Services",
#         type="GP Consultation Service",
#     )

#     assert isinstance(result, HealthcareService)

#     opening_times = [time.model_dump(mode="json") for time in result.openingTime]
#     assert opening_times == [
#         {
#             "category": "availableTime",
#             "dayOfWeek": "mon",
#             "startTime": "09:00:00",
#             "endTime": "17:00:00",
#             "allDay": False,
#         },
#         {
#             "category": "availableTime",
#             "dayOfWeek": "tue",
#             "startTime": "09:00:00",
#             "endTime": "12:00:00",
#             "allDay": False,
#         },
#         {
#             "category": "availableTime",
#             "dayOfWeek": "tue",
#             "startTime": "13:00:00",
#             "endTime": "17:00:00",
#             "allDay": False,
#         },
#         {
#             "category": "availableTime",
#             "dayOfWeek": "fri",
#             "startTime": "09:00:00",
#             "endTime": "17:00:00",
#             "allDay": False,
#         },
#         {
#             "category": "availableTimePublicHolidays",
#             "startTime": "10:00:00",
#             "endTime": "16:00:00",
#         },
#         {
#             "category": "availableTimeVariations",
#             "description": None,
#             "startTime": "2025-07-15T09:00:00",
#             "endTime": "2025-07-15T17:00:00",
#         },
#         {
#             "category": "notAvailable",
#             "description": None,
#             "startTime": "2025-07-16T00:00:00",
#             "endTime": "2025-07-16T23:59:00",
#         },
#     ]

from datetime import UTC, date, datetime, time

import pytest
from freezegun import freeze_time
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    Address,
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    Disposition,
    Endpoint,
    HealthcareService,
    Location,
    NotAvailable,
    Organisation,
    PositionGCS,
    SymptomDiscriminator,
    SymptomGroup,
    SymptomGroupSymptomDiscriminatorPair,
    Telecom,
)
from ftrs_data_layer.domain.legacy import (
    OpeningTimeDay,
    Service,
    ServiceDayOpening,
    ServiceDayOpeningTime,
    ServiceEndpoint,
    ServiceSpecifiedOpeningDate,
    ServiceSpecifiedOpeningTime,
)

from pipeline.transformer import ServiceTransformer


class BasicServiceTransformer(ServiceTransformer):
    def transform(self, service: Service) -> dict:
        return super().transform(service)

    @classmethod
    def is_service_supported(cls, service: Service) -> tuple[bool, str | None]:
        return super().is_service_supported(service)

    @classmethod
    def should_include_service(cls, service: Service) -> tuple[bool, str | None]:
        return super().should_include_service(service)


@freeze_time("2025-07-17T12:00:00")
def test_service_transformer_init(mock_logger: MockLogger) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)

    assert transformer.logger == mock_logger
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


@freeze_time("2025-07-17T12:00:00")
def test_service_transformer_build_organisation(
    mock_logger: MockLogger, mock_legacy_service: Service
) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)
    result = transformer.build_organisation(mock_legacy_service)

    assert isinstance(result, Organisation)
    assert result == Organisation(
        id="4539600c-e04e-5b35-a582-9fb36858d0e0",
        name="Test Service",
        type="GP Practice",
        active=True,
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        identifier_ODS_ODSCode="A12345",
        endpoints=[
            Endpoint(
                id="a226aaa5-392c-59c8-8d79-563bb921cb0d",
                createdBy="DATA_MIGRATION",
                createdDateTime="2025-07-17T12:00:00Z",
                modifiedBy="DATA_MIGRATION",
                modifiedDateTime="2025-07-17T12:00:00Z",
                identifier_oldDoS_id=1,
                status="active",
                connectionType="http",
                name=None,
                payloadMimeType=None,
                description="Primary",
                payloadType="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
                address="http://example.com/endpoint",
                managedByOrganisation="4539600c-e04e-5b35-a582-9fb36858d0e0",
                service=None,
                order=1,
                isCompressionEnabled=True,
            ),
            Endpoint(
                id="4d678d9c-61db-584f-a64c-bd8eb829d8db",
                createdBy="DATA_MIGRATION",
                createdDateTime="2025-07-17T12:00:00Z",
                modifiedBy="DATA_MIGRATION",
                modifiedDateTime="2025-07-17T12:00:00Z",
                identifier_oldDoS_id=2,
                status="active",
                connectionType="email",
                name=None,
                payloadMimeType=None,
                description="Copy",
                payloadType="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
                address="mailto:test@example.com",
                managedByOrganisation="4539600c-e04e-5b35-a582-9fb36858d0e0",
                service=None,
                order=2,
                isCompressionEnabled=False,
            ),
        ],
    )


@freeze_time("2025-07-17T12:00:00")
def test_build_endpoint(
    mock_logger: MockLogger,
) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)

    mock_endpoint = ServiceEndpoint(
        id=12345,
        endpointorder=1,
        transport="itk",
        format="xml",
        interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        businessscenario="Primary",
        address="http://example.com/endpoint1",
        comment="Test Endpoint 1",
        iscompressionenabled="uncompressed",
        serviceid=123456,
    )

    result = transformer.build_endpoint(
        mock_endpoint,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        "01d78de8-4e63-53b3-9b7d-107c39c23a8d",
    )

    assert isinstance(result, Endpoint)
    assert result == Endpoint(
        id="01d78de8-4e63-53b3-9b7d-107c39c23a8d",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        identifier_oldDoS_id=12345,
        status="active",
        connectionType="itk",
        name=None,
        payloadMimeType="xml",
        description="Primary",
        payloadType="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        address="http://example.com/endpoint1",
        managedByOrganisation="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        service="01d78de8-4e63-53b3-9b7d-107c39c23a8d",
        order=1,
        isCompressionEnabled=False,
    )


@freeze_time("2025-07-17T12:00:00")
def test_build_endpoint_telno(mock_logger: MockLogger) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)

    mock_endpoint = ServiceEndpoint(
        id=67890,
        endpointorder=2,
        transport="telno",
        format=None,
        interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        businessscenario="Copy",
        address="tel:01234567890",
        comment="Test Endpoint 2",
        iscompressionenabled=None,
        serviceid=123456,
    )

    result = transformer.build_endpoint(
        mock_endpoint,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        "4f1a685e-15da-5324-b596-6090fc90dc49",
    )

    assert isinstance(result, Endpoint)
    assert result == Endpoint(
        id="4f1a685e-15da-5324-b596-6090fc90dc49",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        identifier_oldDoS_id=67890,
        status="active",
        connectionType="telno",
        name=None,
        payloadMimeType=None,
        description="Copy",
        payloadType=None,
        address="tel:01234567890",
        managedByOrganisation="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        service="4f1a685e-15da-5324-b596-6090fc90dc49",
        order=2,
        isCompressionEnabled=False,
    )


@freeze_time("2025-07-17T12:00:00")
def test_build_location(mock_legacy_service: Service, mock_logger: MockLogger) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)

    result = transformer.build_location(
        mock_legacy_service,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
    )

    assert isinstance(result, Location)
    assert result == Location(
        id="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        active=True,
        managingOrganisation="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        address=Address(
            street="123 Test Street$Test City",
            town="Test City",
            postcode="AB12 3CD",
        ),
        name=None,
        positionGCS=PositionGCS(
            latitude="51.5074",
            longitude="-0.1278",
        ),
        primaryAddress=True,
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        partOf=None,
    )


@freeze_time("2025-07-17T12:00:00")
def test_build_location_no_position(
    mock_legacy_service: Service, mock_logger: MockLogger
) -> None:
    mock_legacy_service.latitude = None
    mock_legacy_service.longitude = None

    transformer = BasicServiceTransformer(logger=mock_logger)

    result = transformer.build_location(
        mock_legacy_service,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
    )

    assert isinstance(result, Location)
    assert result.positionGCS is None
    assert result == Location(
        id="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        active=True,
        managingOrganisation="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        address=Address(
            street="123 Test Street$Test City",
            town="Test City",
            postcode="AB12 3CD",
        ),
        name=None,
        positionGCS=None,
        primaryAddress=True,
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        partOf=None,
    )


@freeze_time("2025-07-25T12:00:00")
def test_build_healthcare_service(
    mock_legacy_service: Service, mock_logger: MockLogger
) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)

    result = transformer.build_healthcare_service(
        mock_legacy_service,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        "6ef3317e-c6dc-5e27-b36d-577c375eb060",
        category="GP Services",
        type="GP Consultation Service",
    )

    assert result == HealthcareService(
        id="903cd48b-5d0f-532f-94f4-937a4517b14d",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-25T12:00:00+00:00",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-25T12:00:00+00:00",
        identifier_oldDoS_uid="test-uid",
        active=True,
        category="GP Services",
        type="GP Consultation Service",
        providedBy="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        location="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        name="Test Service",
        telecom=Telecom(
            phone_public="01234 567890",
            phone_private="09876 543210",
            email="test@example.com",
            web="http://example.com",
        ),
        openingTime=[
            AvailableTime(
                category="availableTime",
                dayOfWeek="mon",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="tue",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="wed",
                startTime="09:00:00",
                endTime="12:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="wed",
                startTime="13:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="thu",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="fri",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="sat",
                startTime="10:00:00",
                endTime="14:00:00",
                allDay=False,
            ),
            AvailableTimePublicHolidays(
                category="availableTimePublicHolidays",
                startTime="10:00:00",
                endTime="14:00:00",
            ),
        ],
        symptomGroupSymptomDiscriminators=[
            SymptomGroupSymptomDiscriminatorPair(
                sg=SymptomGroup(
                    id="d99da436-4a6f-57d9-828d-7a21b8d62a07",
                    source="pathways",
                    codeType="Symptom Group (SG)",
                    codeID=1035,
                    codeValue="Breathing Problems, Breathlessness or Wheeze, Pregnant",
                ),
                sd=SymptomDiscriminator(
                    id="8cf9af7f-d476-5f27-bc40-47c7826a4a17",
                    source="pathways",
                    codeType="Symptom Discriminator (SD)",
                    codeID=4003,
                    codeValue="PC full Primary Care assessment and prescribing capability",
                    synonyms=[],
                ),
            ),
            SymptomGroupSymptomDiscriminatorPair(
                sg=SymptomGroup(
                    id="56138625-05bc-5575-9c9c-b1d390d054d2",
                    source="servicefinder",
                    codeType="Symptom Group (SG)",
                    codeID=360,
                    codeValue="z2.0 - Service Types",
                ),
                sd=SymptomDiscriminator(
                    id="7ff7cb87-baf5-541a-9139-f85eab0bc312",
                    source="servicefinder",
                    codeType="Symptom Discriminator (SD)",
                    codeID=14023,
                    codeValue="GP Practice",
                    synonyms=["General Practice"],
                ),
            ),
        ],
        dispositions=[
            Disposition(
                id="4443b15a-26a3-517f-8a93-eb7c2539d4fc",
                source="pathways",
                codeType="Disposition (Dx)",
                codeID=126,
                codeValue="Contact Own GP Practice next working day for appointment",
                time=7200,
            ),
            Disposition(
                id="ae7a129f-cda2-51f6-aff6-88a94f7f36de",
                source="pathways",
                codeType="Disposition (Dx)",
                codeID=10,
                codeValue="Speak to a Primary Care Service within 2 hours",
                time=120,
            ),
        ],
    )


def test_build_opening_times(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)

    mock_legacy_service.scheduled_opening_times = [
        ServiceDayOpening(
            id=1,
            serviceid=1,
            dayid=1,
            day=OpeningTimeDay(id=1, name="Monday"),
            times=[
                ServiceDayOpeningTime(
                    id=1,
                    starttime=time.fromisoformat("09:00:00"),
                    endtime=time.fromisoformat("17:00:00"),
                    servicedayopeningid=1,
                )
            ],
        ),
        ServiceDayOpening(
            id=2,
            serviceid=1,
            dayid=8,
            day=OpeningTimeDay(id=8, name="BankHoliday"),
            times=[
                ServiceDayOpeningTime(
                    id=2,
                    starttime=time.fromisoformat("10:00:00"),
                    endtime=time.fromisoformat("16:00:00"),
                    servicedayopeningid=2,
                )
            ],
        ),
    ]

    mock_legacy_service.specified_opening_times = [
        ServiceSpecifiedOpeningDate(
            id=1,
            serviceid=1,
            date=date.fromisoformat("2025-07-15"),
            times=[
                ServiceSpecifiedOpeningTime(
                    id=1,
                    isclosed=False,
                    starttime=time.fromisoformat("08:00:00"),
                    endtime=time.fromisoformat("12:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
                ServiceSpecifiedOpeningTime(
                    id=2,
                    isclosed=False,
                    starttime=time.fromisoformat("13:00:00"),
                    endtime=time.fromisoformat("18:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
            ],
        ),
        ServiceSpecifiedOpeningDate(
            id=2,
            serviceid=1,
            date=date.fromisoformat("2025-07-16"),
            times=[
                ServiceSpecifiedOpeningTime(
                    id=3,
                    isclosed=True,
                    starttime=time.fromisoformat("00:00:00"),
                    endtime=time.fromisoformat("23:59:59"),
                    servicespecifiedopeningdateid=2,
                )
            ],
        ),
    ]

    result = transformer.build_opening_times(mock_legacy_service)

    assert isinstance(result, list)
    assert result == [
        AvailableTime(
            category="availableTime",
            dayOfWeek="mon",
            startTime=time(9, 0),
            endTime=time(17, 0),
            allDay=False,
        ),
        AvailableTimePublicHolidays(
            category="availableTimePublicHolidays",
            startTime=time(10, 0),
            endTime=time(16, 0),
        ),
        AvailableTimeVariation(
            category="availableTimeVariations",
            description=None,
            startTime=datetime(2025, 7, 15, 8, 0),
            endTime=datetime(2025, 7, 15, 12, 0),
        ),
        AvailableTimeVariation(
            category="availableTimeVariations",
            description=None,
            startTime=datetime(2025, 7, 15, 13, 0),
            endTime=datetime(2025, 7, 15, 18, 0),
        ),
        NotAvailable(
            category="notAvailable",
            description=None,
            startTime=datetime(2025, 7, 16, 0, 0),
            endTime=datetime(2025, 7, 16, 23, 59, 59),
        ),
    ]


def test_build_scheduled_opening_times(
    mock_legacy_service: Service, mock_logger: MockLogger
) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)

    mock_legacy_service.scheduled_opening_times = [
        ServiceDayOpening(
            id=1,
            serviceid=1,
            dayid=1,
            day=OpeningTimeDay(id=1, name="Monday"),
            times=[
                ServiceDayOpeningTime(
                    id=1,
                    starttime=time.fromisoformat("09:00:00"),
                    endtime=time.fromisoformat("17:00:00"),
                    servicedayopeningid=1,
                )
            ],
        ),
        ServiceDayOpening(
            id=2,
            serviceid=1,
            dayid=8,
            day=OpeningTimeDay(id=8, name="BankHoliday"),
            times=[
                ServiceDayOpeningTime(
                    id=2,
                    starttime=time.fromisoformat("10:00:00"),
                    endtime=time.fromisoformat("16:00:00"),
                    servicedayopeningid=2,
                )
            ],
        ),
    ]

    result = transformer.build_scheduled_opening_times(
        mock_legacy_service.scheduled_opening_times
    )

    assert isinstance(result, list)
    assert result == [
        AvailableTime(
            category="availableTime",
            dayOfWeek="mon",
            startTime=time(9, 0),
            endTime=time(17, 0),
            allDay=False,
        ),
        AvailableTimePublicHolidays(
            category="availableTimePublicHolidays",
            startTime=time(10, 0),
            endTime=time(16, 0),
        ),
    ]


def test_build_specified_opening_times(
    mock_legacy_service: Service, mock_logger: MockLogger
) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)

    mock_legacy_service.specified_opening_times = [
        ServiceSpecifiedOpeningDate(
            id=1,
            serviceid=1,
            date=date.fromisoformat("2025-07-15"),
            times=[
                ServiceSpecifiedOpeningTime(
                    id=1,
                    isclosed=False,
                    starttime=time.fromisoformat("08:00:00"),
                    endtime=time.fromisoformat("12:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
                ServiceSpecifiedOpeningTime(
                    id=2,
                    isclosed=False,
                    starttime=time.fromisoformat("13:00:00"),
                    endtime=time.fromisoformat("18:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
            ],
        ),
        ServiceSpecifiedOpeningDate(
            id=2,
            serviceid=1,
            date=date.fromisoformat("2025-07-16"),
            times=[
                ServiceSpecifiedOpeningTime(
                    id=3,
                    isclosed=True,
                    starttime=time.fromisoformat("00:00:00"),
                    endtime=time.fromisoformat("23:59:59"),
                    servicespecifiedopeningdateid=2,
                )
            ],
        ),
    ]

    result = transformer.build_specified_opening_times(
        mock_legacy_service.specified_opening_times
    )

    assert isinstance(result, list)
    assert result == [
        AvailableTimeVariation(
            category="availableTimeVariations",
            description=None,
            startTime=datetime(2025, 7, 15, 8, 0),
            endTime=datetime(2025, 7, 15, 12, 0),
        ),
        AvailableTimeVariation(
            category="availableTimeVariations",
            description=None,
            startTime=datetime(2025, 7, 15, 13, 0),
            endTime=datetime(2025, 7, 15, 18, 0),
        ),
        NotAvailable(
            category="notAvailable",
            description=None,
            startTime=datetime(2025, 7, 16, 0, 0),
            endTime=datetime(2025, 7, 16, 23, 59, 59),
        ),
    ]


def test_build_sgsds(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)
    result = transformer.build_sgsds(mock_legacy_service)

    assert isinstance(result, list)
    assert result == [
        SymptomGroupSymptomDiscriminatorPair(
            sg=SymptomGroup(
                id="d99da436-4a6f-57d9-828d-7a21b8d62a07",
                source="pathways",
                codeType="Symptom Group (SG)",
                codeID=1035,
                codeValue="Breathing Problems, Breathlessness or Wheeze, Pregnant",
            ),
            sd=SymptomDiscriminator(
                id="8cf9af7f-d476-5f27-bc40-47c7826a4a17",
                source="pathways",
                codeType="Symptom Discriminator (SD)",
                codeID=4003,
                codeValue="PC full Primary Care assessment and prescribing capability",
                synonyms=[],
            ),
        ),
        SymptomGroupSymptomDiscriminatorPair(
            sg=SymptomGroup(
                id="56138625-05bc-5575-9c9c-b1d390d054d2",
                source="servicefinder",
                codeType="Symptom Group (SG)",
                codeID=360,
                codeValue="z2.0 - Service Types",
            ),
            sd=SymptomDiscriminator(
                id="7ff7cb87-baf5-541a-9139-f85eab0bc312",
                source="servicefinder",
                codeType="Symptom Discriminator (SD)",
                codeID=14023,
                codeValue="GP Practice",
                synonyms=["General Practice"],
            ),
        ),
    ]


def test_build_dispositions(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
) -> None:
    transformer = BasicServiceTransformer(logger=mock_logger)
    result = transformer.build_dispositions(mock_legacy_service)

    assert isinstance(result, list)
    assert result == [
        Disposition(
            id="4443b15a-26a3-517f-8a93-eb7c2539d4fc",
            source="pathways",
            codeType="Disposition (Dx)",
            codeID=126,
            codeValue="Contact Own GP Practice next working day for appointment",
            time=7200,
        ),
        Disposition(
            id="ae7a129f-cda2-51f6-aff6-88a94f7f36de",
            source="pathways",
            codeType="Disposition (Dx)",
            codeID=10,
            codeValue="Speak to a Primary Care Service within 2 hours",
            time=120,
        ),
    ]
