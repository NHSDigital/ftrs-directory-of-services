from abc import ABC, abstractmethod
from datetime import UTC, datetime
from decimal import Decimal
from typing import Type
from uuid import UUID

from ftrs_common.logger import Logger
from ftrs_data_layer.domain import (
    PAYLOAD_MIMETYPE_MAPPING,
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    Endpoint,
    EndpointStatus,
    HealthcareService,
    HealthcareServiceCategory,
    HealthcareServiceTelecom,
    HealthcareServiceType,
    Location,
    NotAvailable,
    OpeningTime,
    Organisation,
    PositionGCS,
)
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from ftrs_data_layer.domain.clinical_code import (
    Disposition,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.enums import TimeUnit
from ftrs_data_layer.logbase import DataMigrationLogBase
from pydantic import BaseModel, Field

from common.cache import DoSMetadataCache
from common.uuid_utils import generate_uuid
from service_migration.formatting.address_formatter import format_address
from service_migration.formatting.number_formatter import clean_decimal
from service_migration.validation.base import Validator
from service_migration.validation.service import ServiceValidator


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

    def __init__(self, logger: Logger, metadata: DoSMetadataCache) -> None:
        self.start_time = datetime.now(UTC)
        self.logger = logger
        self.metadata = metadata
        self.validator = self.VALIDATOR_CLS(logger)

    @abstractmethod
    def transform(self, service: legacy_model.Service) -> ServiceTransformOutput:
        """
        Transform the given service data into a dictionary format.

        :param validation_issues:
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

    def build_organisation(
        self,
        service: legacy_model.Service,
    ) -> Organisation:
        """
        Create an Organisation instance from the source DoS service data.
        """
        organisation_id = generate_uuid(service.id, "organisation")
        service_type = self.metadata.service_types.get(service.typeid)

        return Organisation(
            id=organisation_id,
            identifier_oldDoS_uid=service.uid,
            identifier_ODS_ODSCode=service.odscode,
            active=True,
            name=service.name,
            telecom=[],
            type=service_type.name,
            createdBy=self.MIGRATION_USER,
            createdTime=self.start_time,
            lastUpdatedBy=self.MIGRATION_USER,
            lastUpdated=self.start_time,
            endpoints=[
                self.build_endpoint(endpoint, organisation_id)
                for endpoint in service.endpoints
            ],
        )

    def build_endpoint(
        self,
        endpoint: legacy_model.ServiceEndpoint,
        organisation_id: UUID,
        service_id: UUID | None = None,
    ) -> Endpoint:
        """
        Create an Endpoint instance from the source DoS endpoint data.
        """
        payload_type = endpoint.interaction
        payload_mime_type = PAYLOAD_MIMETYPE_MAPPING.get(
            endpoint.format, endpoint.format
        )

        if endpoint.transport == "telno":
            payload_type = None
            payload_mime_type = None

        return Endpoint(
            id=generate_uuid(endpoint.id, "endpoint"),
            identifier_oldDoS_id=endpoint.id,
            status=EndpointStatus.ACTIVE,
            connectionType=endpoint.transport,
            name=None,
            businessScenario=endpoint.businessscenario,
            payloadType=payload_type,
            payloadMimeType=payload_mime_type,
            address=endpoint.address,
            managedByOrganisation=organisation_id,
            service=service_id,
            order=endpoint.endpointorder,
            isCompressionEnabled=endpoint.iscompressionenabled == "compressed",
            createdBy=self.MIGRATION_USER,
            createdTime=self.start_time,
            lastUpdatedBy=self.MIGRATION_USER,
            lastUpdated=self.start_time,
            comment=endpoint.comment,
        )

    def build_location(
        self,
        service: legacy_model.Service,
        organisation_id: UUID,
    ) -> Location | None:
        """
        Create a Location instance from the source DoS service data if address is valid.
        """
        position = (
            PositionGCS(
                latitude=service.latitude,
                longitude=service.longitude,
            )
            if service.latitude and service.longitude
            else None
        )

        formatted_address = format_address(
            service.address,
            service.town,
            service.postcode,
        )

        return Location(
            id=generate_uuid(service.id, "location"),
            identifier_oldDoS_uid=service.uid,
            active=True,
            managingOrganisation=organisation_id,
            address=formatted_address,
            name=None,
            positionGCS=position,
            # TODO: defaulting will consider how to define for Fhir schema in future.
            #   but since this has the main ODSCode happy with this being set as True
            primaryAddress=True,
            createdBy=self.MIGRATION_USER,
            createdTime=self.start_time,
            lastUpdatedBy=self.MIGRATION_USER,
            lastUpdated=self.start_time,
        )

    def build_healthcare_service(
        self,
        service: legacy_model.Service,
        organisation_id: UUID,
        location_id: UUID,
        category: HealthcareServiceCategory | None = None,
        type: HealthcareServiceType | None = None,
    ) -> HealthcareService:
        """
        Create a HealthcareService instance from the source DoS service data.
        """

        return HealthcareService(
            id=generate_uuid(service.id, "healthcare_service"),
            identifier_oldDoS_uid=service.uid,
            active=True,
            category=category,
            type=type,
            providedBy=organisation_id,
            location=location_id,
            name=service.name,
            telecom=HealthcareServiceTelecom(
                phone_public=service.publicphone,
                phone_private=service.nonpublicphone,
                email=service.email,
                web=service.web,
            ),
            createdBy=self.MIGRATION_USER,
            createdTime=self.start_time,
            lastUpdatedBy=self.MIGRATION_USER,
            lastUpdated=self.start_time,
            openingTime=self.build_opening_times(service),
            symptomGroupSymptomDiscriminators=self.build_sgsds(service),
            dispositions=self.build_dispositions(service),
            ageEligibilityCriteria=self.build_age_eligibility_criteria(service),
        )

    def build_opening_times(self, service: legacy_model.Service) -> list[dict]:
        """
        Build opening times from the service's scheduled opening times.
        """
        scheduled_times = self.build_scheduled_opening_times(
            service.scheduled_opening_times
        )
        specified_times = self.build_specified_opening_times(
            service.specified_opening_times
        )
        return scheduled_times + specified_times

    def build_scheduled_opening_times(
        self, service_day_openings: list[legacy_model.ServiceDayOpening]
    ) -> list[OpeningTime]:
        """
        Build scheduled opening times from the service's scheduled opening times.
        """
        items = []
        for day_opening in service_day_openings:
            availability_cls = AvailableTime
            day = self.metadata.opening_time_days.get(day_opening.dayid)
            day_of_week = day.name.lower()[:3]

            if day.name == "BankHoliday":
                availability_cls = AvailableTimePublicHolidays
                day_of_week = None

            items.extend(
                [
                    availability_cls(
                        dayOfWeek=day_of_week,
                        startTime=opening_time.starttime,
                        endTime=opening_time.endtime,
                        allDay=False,
                    )
                    for opening_time in day_opening.times
                ]
            )

        return items

    def build_specified_opening_times(
        self,
        service_specified_opening_dates: list[legacy_model.ServiceSpecifiedOpeningDate],
    ) -> list[OpeningTime]:
        """
        Build specified opening times from the service's specified opening times.
        """
        items = []
        for specified_date in service_specified_opening_dates:
            for specified_time in specified_date.times:
                availability_cls = AvailableTimeVariation
                if specified_time.isclosed:
                    availability_cls = NotAvailable

                items.append(
                    availability_cls(
                        startTime=datetime.combine(
                            specified_date.date, specified_time.starttime
                        ),
                        endTime=datetime.combine(
                            specified_date.date, specified_time.endtime
                        ),
                    )
                )

        return items

    def build_sgsds(
        self, service: legacy_model.Service
    ) -> list[SymptomGroupSymptomDiscriminatorPair]:
        return [self.build_sgsd_pair(code) for code in service.sgsds]

    def build_sgsd_pair(
        self, code: legacy_model.ServiceSGSD
    ) -> SymptomGroupSymptomDiscriminatorPair:
        """
        Build a single SymptomGroupSymptomDiscriminatorPair from a ServiceSGSD code.
        """
        return SymptomGroupSymptomDiscriminatorPair(
            sg=code.sgid,
            sd=code.sdid,
        )

    def build_dispositions(self, service: legacy_model.Service) -> list[Disposition]:
        """
        Build dispositions from the service's dispositions.
        """
        dispositions = []
        for code in service.dispositions:
            disposition = self.build_disposition(code, service.id)
            if disposition is not None:
                dispositions.append(disposition)
        return dispositions

    def build_disposition(
        self, code: legacy_model.ServiceDisposition, service_id: int
    ) -> str | None:
        """
        Build a single Disposition from a ServiceDisposition code.
        Returns None if the disposition is not found in metadata.
        """
        disposition = self.metadata.dispositions.get(code.dispositionid)
        if disposition is None:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_018,
                service_id=service_id,
                disposition_id=code.dispositionid,
            )
            return None
        return disposition.dxcode

    def build_age_eligibility_criteria(
        self, service: legacy_model.Service
    ) -> list | None:
        """
        Build age eligibility criteria from the service's age ranges, in days.
        * Where there are multiple consecutive age ranges, these should be combined to a single range.
        * Where there are multiple non consecutive age ranges, these should each be an item in the list.

        It handles standard DoS age groups (in days):
        * 0-364.25, 365.25-1825.25, 1826.25-5843, 5844-47481.5
        * Two ranges are consecutive if the end of one is very close to the start of the next.
        * Tolerance of 1 day is used to determine if ranges are consecutive.
        """
        if not service.age_range:
            self.logger.log(DataMigrationLogBase.DM_ETL_017, service_id=service.id)
            return None

        TOLERANCE = Decimal(1)

        sorted_ranges = sorted(service.age_range, key=lambda x: x.daysfrom)

        result = []
        current_range = {
            "rangeFrom": clean_decimal(sorted_ranges[0].daysfrom),
            "rangeTo": clean_decimal(sorted_ranges[0].daysto),
            "type": TimeUnit.DAYS,
        }

        for age_range in sorted_ranges[1:]:
            current_end = current_range["rangeTo"]
            next_start = age_range.daysfrom
            next_end = age_range.daysto
            # Check if ranges are consecutive
            if abs(next_start - current_end) <= TOLERANCE:
                # Extend the current range to include this range
                current_range["rangeTo"] = clean_decimal(next_end)
            # Check if ranges overlap
            elif next_start <= current_end:
                # If the next range starts before the current one ends,
                # extend the current range if needed
                if next_end > current_end:
                    current_range["rangeTo"] = clean_decimal(next_end)
            else:
                # Non-consecutive range - add the current range to the result
                # and start a new one
                result.append(current_range)
                current_range = {
                    "rangeFrom": clean_decimal(next_start),
                    "rangeTo": clean_decimal(next_end),
                    "type": TimeUnit.DAYS,
                }

        result.append(current_range)

        return result
