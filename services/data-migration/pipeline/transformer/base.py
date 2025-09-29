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
    HealthcareServiceType,
    Location,
    NotAvailable,
    OpeningTime,
    Organisation,
    PositionGCS,
    Telecom,
)
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.domain.clinical_code import (
    ClinicalCodeSource,
    Disposition,
    SymptomDiscriminator,
    SymptomGroup,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.logbase import DataMigrationLogBase
from pydantic import BaseModel, Field

from pipeline.utils.address_formatter import format_address
from pipeline.utils.cache import DoSMetadataCache
from pipeline.utils.uuid_utils import generate_uuid
from pipeline.validation.base import Validator
from pipeline.validation.service import ServiceValidator


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
    MIGRATION_USER = "DATA_MIGRATION"
    VALIDATOR_CLS: Type[Validator] = ServiceValidator

    def __init__(self, logger: Logger, metadata: DoSMetadataCache) -> None:
        self.start_time = datetime.now(UTC)
        self.logger = logger
        self.metadata = metadata
        self.validator = self.VALIDATOR_CLS(logger)

    @abstractmethod
    def transform(
        self, service: legacy_model.Service, validation_issues: list[str]
    ) -> ServiceTransformOutput:
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
            identifier_ODS_ODSCode=service.odscode,
            active=True,
            name=service.name,
            telecom=None,
            type=service_type.name,
            createdBy=self.MIGRATION_USER,
            createdDateTime=self.start_time,
            modifiedBy=self.MIGRATION_USER,
            modifiedDateTime=self.start_time,
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
            description=endpoint.businessscenario,
            payloadType=payload_type,
            payloadMimeType=payload_mime_type,
            address=endpoint.address,
            managedByOrganisation=organisation_id,
            service=service_id,
            order=endpoint.endpointorder,
            isCompressionEnabled=endpoint.iscompressionenabled == "compressed",
            createdBy=self.MIGRATION_USER,
            createdDateTime=self.start_time,
            modifiedBy=self.MIGRATION_USER,
            modifiedDateTime=self.start_time,
        )

    def build_location(
        self,
        service: legacy_model.Service,
        organisation_id: UUID,
    ) -> Location:
        """
        Create a Location instance from the source DoS service data.
        """
        position = (
            PositionGCS(
                latitude=service.latitude,
                longitude=service.longitude,
            )
            if service.latitude and service.longitude
            else None
        )
        if service.address and service.address != "Not Available":
            formatted_address = format_address(
                service.address, service.town, service.postcode
            )
            self.logger.log(
                DataMigrationLogBase.DM_ETL_015,
                organisation=organisation_id,
                address=formatted_address,
            )

        else:
            formatted_address = None
            self.logger.log(
                DataMigrationLogBase.DM_ETL_016, organisation=organisation_id
            )

        return Location(
            id=generate_uuid(service.id, "location"),
            active=True,
            managingOrganisation=organisation_id,
            address=formatted_address,
            name=None,
            positionGCS=position,
            # TODO: defaulting will consider how to define for Fhir schema in future.
            #   but since this has the main ODSCode happy with this being set as True
            primaryAddress=True,
            createdBy=self.MIGRATION_USER,
            createdDateTime=self.start_time,
            modifiedBy=self.MIGRATION_USER,
            modifiedDateTime=self.start_time,
        )

    # TODO: FDOS-383 - add ageEligibilityCriteria field
    # * Where a service profile has an age range assigned,
    # * * this should be imported and linked to the healthcare service in the "ageEligibilityCriteria" field.
    # * Age range data on imported healthcare services is imported and linked correctly to each service
    def build_healthcare_service(
        self,
        service: legacy_model.Service,
        organisation_id: UUID,
        location_id: UUID,
        category: HealthcareServiceCategory | None = None,
        type: HealthcareServiceType | None = None,
        validation_issues: list[str] | None = None,
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
            telecom=Telecom(
                phone_public=service.publicphone,
                phone_private=service.nonpublicphone,
                email=service.email,
                web=service.web,
            ),
            createdBy=self.MIGRATION_USER,
            createdDateTime=self.start_time,
            modifiedBy=self.MIGRATION_USER,
            modifiedDateTime=self.start_time,
            openingTime=self.build_opening_times(service),
            symptomGroupSymptomDiscriminators=self.build_sgsds(service),
            dispositions=self.build_dispositions(service),
            migrationNotes=validation_issues,
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
        sg = self.metadata.symptom_groups.get(code.sgid)
        sd = self.metadata.symptom_discriminators.get(code.sdid)

        source = (
            ClinicalCodeSource.SERVICE_FINDER
            if sg.zcodeexists is True
            else ClinicalCodeSource.PATHWAYS
        )

        return SymptomGroupSymptomDiscriminatorPair(
            sg=SymptomGroup(
                id=generate_uuid(sg.id, "symptomgroup"),
                codeID=code.sgid,
                codeValue=sg.name,
                source=source,
            ),
            sd=SymptomDiscriminator(
                id=generate_uuid(sd.id, "symptomdiscriminator"),
                codeID=code.sdid,
                codeValue=sd.description,
                source=source,
                synonyms=[syn.name for syn in sd.synonyms],
            ),
        )

    def build_dispositions(self, service: legacy_model.Service) -> list[Disposition]:
        """
        Build dispositions from the service's dispositions.
        """
        return [self.build_disposition(code) for code in service.dispositions]

    def build_disposition(self, code: legacy_model.ServiceDisposition) -> Disposition:
        """
        Build a single Disposition from a ServiceDisposition code.
        """
        disposition = self.metadata.dispositions.get(code.dispositionid)
        return Disposition(
            id=generate_uuid(code.id, "pathways:disposition"),
            codeID=code.dispositionid,
            codeValue=disposition.name,
            source=ClinicalCodeSource.PATHWAYS,
            time=disposition.dispositiontime,
        )

    # TODO: FDOS-383 - add function to build ageEligibilityCriteria
    # * Where there are multiple consecutive age ranges, these should be combined to a single range.
    # * Where there are multiple non consecutive age ranges, these should each be an item in the list.
    # * Values copied across, should all be in type "days"
    def build_age_eligibility_criteria(
        self, service: legacy_model.Service
    ) -> list | None:
        """
        Build age eligibility criteria from the service's age ranges.

        This method processes legacy age ranges and converts them to the new format.
        It handles standard DoS age groups, for example:
            * 0-364.25 days
            * 365.25-1825.25 days
            * 1826.25-5843 days
            * 5844-47481.5 days

        Examples of output:
            For a service with age ranges 0-364.25 and 365.25-1825.25, returns:
            [{"range": {"rangeFrom": 0, "rangeTo": 1825.25}, "type": "days"}]
            For a service with age ranges 0-364.25 and 1826.25-5843, returns:
            [{"range": {"rangeFrom": 0, "rangeTo": 364.25}, "type": "days"},
            {"range": {"rangeFrom": 1826.25, "rangeTo": 5843}, "type": "days"}]
            For a service with no age ranges, returns None and logs this fact.
            For a service with age ranges, 0-364.25, 365.25-1825.25, 1826.25-5843, 5844-47481.5, 23741.25-47481.5 returns:
            [{"range": {"rangeFrom": 0, "rangeTo": 47481.5}, "type": "days"}]
        """
        # Check if there are any age ranges to process, return None if not and log this fact
        if not service.age_range:
            self.logger.log(DataMigrationLogBase.DM_ETL_017, service_id=service.id)
            return None

        # Define a small tolerance for comparing Decimal values
        # This helps handle floating point comparison issues
        TOLERANCE = Decimal("1")

        # Sort age ranges by their start day (daysfrom)
        sorted_ranges = sorted(service.age_range, key=lambda x: x.daysfrom)

        # Initialize result list and the first range
        result = []
        if not sorted_ranges:
            return result

        # Start with the first range
        current_range = {
            "range": {
                "rangeFrom": sorted_ranges[0].daysfrom,
                "rangeTo": sorted_ranges[0].daysto,
            },
            "type": "days",
        }

        # Process each subsequent range
        for age_range in sorted_ranges[1:]:
            # Get the current end value and the next start value
            current_end = current_range["range"]["rangeTo"]
            next_start = age_range.daysfrom
            next_end = age_range.daysto

            # Check if ranges are consecutive
            # Two ranges are consecutive if the end of one is very close to the start of the next
            if abs(next_start - current_end) <= TOLERANCE:
                # Extend the current range to include this range
                current_range["range"]["rangeTo"] = next_end
            # Check if ranges overlap
            elif next_start <= current_end:
                # If the next range starts before the current one ends,
                # extend the current range if needed
                if next_end > current_end:
                    current_range["range"]["rangeTo"] = next_end
            else:
                # Non-consecutive range - add the current range to the result
                # and start a new one
                result.append(current_range)
                current_range = {
                    "range": {"rangeFrom": next_start, "rangeTo": next_end},
                    "type": "days",
                }

        # Add the final range
        result.append(current_range)

        # return consolidated ranges
        return result
