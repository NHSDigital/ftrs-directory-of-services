from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import UUID, uuid5

from ftrs_common.logger import Logger
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.domain.clinical_code import (
    SymptomGroupSymptomDiscriminatorPair,
    SymptomDiscriminator,
    SymptomGroup,
    Disposition,
    ClinicalCodeSource,
)
from ftrs_data_layer.models import (
    PAYLOAD_MIMETYPE_MAPPING,
    Address,
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
from pydantic import BaseModel
from pipeline.utils.metadata import DoSReferenceData


class ServiceTransformOutput(BaseModel):
    """
    Represents the output of a service transformation.

    This may be adapted in the future to better reflect relationships/data deduplication.
    """

    organisation: Organisation
    healthcare_service: HealthcareService
    location: Location


class ServiceTransformer(ABC):
    """
    Abstract base class for transforming service data.
    """

    MIGRATION_UUID_NS = UUID("fa3aaa15-9f83-4f4a-8f86-fd1315248bcb")
    MIGRATION_USER = "DATA_MIGRATION"

    def __init__(self, reference_data: DoSReferenceData, logger: Logger) -> None:
        self.start_time = datetime.now(UTC)
        self.logger = logger
        self.reference_data = reference_data

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

    def build_organisation(
        self,
        service: legacy_model.Service,
    ) -> Organisation:
        """
        Create an Organisation instance from the source DoS service data.
        """
        organisation_id = self.generate_id(service.id, "organisation")
        return Organisation(
            id=organisation_id,
            identifier_ODS_ODSCode=service.odscode,
            active=True,
            name=service.name,
            telecom=None,
            type=service.type.name,
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
            id=self.generate_id(endpoint.id, "endpoint"),
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

        return Location(
            id=self.generate_id(service.id, "location"),
            active=True,
            managingOrganisation=organisation_id,
            address=Address(
                street=service.address,
                town=service.town,
                postcode=service.postcode,
            ),
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
            id=self.generate_id(service.id, "healthcare_service"),
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
            day_of_week = day_opening.day.name.lower()[:3]

            if day_opening.day.name == "BankHoliday":
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
        return [
            SymptomGroupSymptomDiscriminatorPair(
                sg=SymptomGroup(
                    id=self.generate_id(code.id, "pathways:sg"),
                    codeID=code.sgid,
                    codeValue=code.group.name,
                    source=(
                        ClinicalCodeSource.SERVICE_FINDER
                        if code.group.zcodeexists
                        else ClinicalCodeSource.PATHWAYS
                    ),
                ),
                sd=SymptomDiscriminator(
                    id=self.generate_id(code.id, "pathways:sd"),
                    codeID=code.sdid,
                    codeValue=code.discriminator.description,
                    source=(
                        ClinicalCodeSource.SERVICE_FINDER
                        if code.group.zcodeexists
                        else ClinicalCodeSource.PATHWAYS
                    ),
                    synonyms=[syn.name for syn in code.discriminator.synonyms],
                ),
            )
            for code in service.sgsds
        ]

    def build_dispositions(self, service: legacy_model.Service) -> list[Disposition]:
        """
        Build dispositions from the service's dispositions.
        """
        return [
            Disposition(
                id=self.generate_id(code.id, "pathways:disposition"),
                codeID=code.dispositionid,
                codeValue=code.disposition.name,
                source=ClinicalCodeSource.PATHWAYS,
                time=code.disposition.dispositiontime,
            )
            for code in service.dispositions
        ]

    def generate_id(self, service_id: int, namespace: str) -> UUID:
        """
        Generate a namespaced UUID for the service using the service ID and namespace.
        """
        return uuid5(self.MIGRATION_UUID_NS, f"{namespace}-{service_id}")
