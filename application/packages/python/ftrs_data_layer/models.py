from datetime import UTC, date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Annotated, Literal, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DBModel(BaseModel):
    """
    Base model for all database models.
    """

    id: UUID
    createdBy: str
    createdDateTime: datetime
    modifiedBy: str
    modifiedDateTime: datetime

    @property
    def indexes(self) -> dict:
        """
        Return the indexes for the model.
        This is a placeholder and should be overridden in subclasses.
        """
        return {}

    @classmethod
    def from_dos(
        cls,
        data: dict,
        existing_identifier: UUID | str | None = None,
        created_datetime: datetime | None = None,
        updated_datetime: datetime | None = None,
    ) -> "DBModel":
        """
        Create an instance of the model from source DoS data.

        :param data: The source data dictionary.
        :param created_datetime: The datetime when the object was created.
        :param updated_datetime: The datetime when the object was last updated.
        :return: An instance of the model.
        """
        raise NotImplementedError(f"{cls.__name__}.from_dos method is not implemented.")


class Organisation(DBModel):
    identifier_ODS_ODSCode: str | None = None
    active: bool
    name: str
    telecom: str | None = None
    type: str
    endpoints: list["Endpoint"] = Field(default_factory=list)

    @property
    def indexes(self) -> dict:
        """
        Return the indexes for the Organisation model.
        """
        return {
            "identifier_ODS_ODSCode": self.identifier_ODS_ODSCode,
        }

    @classmethod
    def from_dos(
        cls,
        data: dict,
        existing_identifier: UUID | str | None = None,
        created_datetime: datetime | None = None,
        updated_datetime: datetime | None = None,
    ) -> "Organisation":
        """
        Create an Organisation instance from source DoS data.

        :param data: The source data dictionary from the 'services' DoS table.
        :param created_datetime: The datetime when the organisation was created.
        :param updated_datetime: The datetime when the organisation was last updated.
        :return: An Organisation instance.
        """
        org_id = uuid4() or existing_identifier
        return Organisation(
            id=org_id,
            identifier_ODS_ODSCode=data["odscode"],
            active=True,
            name=data["name"],
            telecom=None,
            type=data["type"],
            createdBy="ROBOT",
            createdDateTime=created_datetime or datetime.now(UTC),
            modifiedBy="ROBOT",
            modifiedDateTime=updated_datetime or datetime.now(UTC),
            endpoints=[
                Endpoint.from_dos(
                    endpoint,
                    managed_by_id=org_id,
                    created_datetime=created_datetime,
                    updated_datetime=updated_datetime,
                )
                for endpoint in data["endpoints"]
            ],
        )


class Address(BaseModel):
    street: str | None
    town: str | None
    postcode: str | None


class PositionGCS(BaseModel):
    latitude: Decimal
    longitude: Decimal

    @classmethod
    def from_dos(
        cls, latitude: Decimal | None, longitude: Decimal | None
    ) -> Optional["Location"]:
        if latitude is None and longitude is None:
            return None
        elif latitude.is_nan() and longitude.is_nan():
            return None
        elif latitude.is_nan() or longitude.is_nan():
            err_msg = "provide both latitude and longitude"
            raise ValueError(err_msg)

        return PositionGCS(latitude=latitude, longitude=longitude)


class Location(DBModel):
    active: bool
    address: Address
    managingOrganisation: UUID
    name: str | None = None
    positionGCS: PositionGCS | None = None
    positionReferenceNumber_UPRN: int | None = None
    positionReferenceNumber_UBRN: int | None = None
    primaryAddress: bool
    partOf: UUID | None = None

    @classmethod
    def from_dos(
        cls,
        data: dict,
        existing_identifier: UUID | str | None = None,
        created_datetime: datetime | None = None,
        updated_datetime: datetime | None = None,
        organisation_id: UUID | None = None,
    ) -> "Location":
        """
        Create an Location instance from source DoS data.

        :param data: The source data dictionary from the 'services' DoS table.
        :param created_datetime: The datetime when the location was created.
        :param updated_datetime: The datetime when the location was last updated.
        :param organisation_id: The managing organisation of the location.
        :return: An Organisation instance.
        """
        location_id = uuid4() or existing_identifier
        return Location(
            id=location_id,
            active=True,
            managingOrganisation=organisation_id,
            address=Address(
                street=data["address"],
                town=data["town"],
                postcode=data["postcode"],
            ),
            name=None,
            positionGCS=PositionGCS.from_dos(
                latitude=Decimal(data["latitude"]),
                longitude=Decimal(data["longitude"]),
            ),
            # TODO: defaulting will consider how to define for Fhir schema in future.
            #   but since this has the main ODSCode happy with this being set as True
            primaryAddress=True,
            createdBy="ROBOT",
            createdDateTime=created_datetime or datetime.now(UTC),
            modifiedBy="ROBOT",
            modifiedDateTime=updated_datetime or datetime.now(UTC),
        )


class Telecom(BaseModel):
    phone_public: str | None
    phone_private: str | None
    email: str | None
    web: str | None


class OpeningTimeCategory(str, Enum):
    AVAILABLE_TIME = "availableTime"
    AVAILABLE_TIME_VARIATIONS = "availableTimeVariations"
    AVAILABLE_TIME_PUBLIC_HOLIDAYS = "availableTimePublicHolidays"
    NOT_AVAILABLE = "notAvailable"


class DayOfWeek(str, Enum):
    MONDAY = "mon"
    TUESDAY = "tue"
    WEDNESDAY = "wed"
    THURSDAY = "thu"
    FRIDAY = "fri"
    SATURDAY = "sat"
    SUNDAY = "sun"


class AvailableTime(BaseModel):
    id: UUID = uuid4()
    category: Literal[OpeningTimeCategory.AVAILABLE_TIME] = (
        OpeningTimeCategory.AVAILABLE_TIME
    )
    dayOfWeek: DayOfWeek
    startTime: time
    endTime: time
    allDay: bool = False


class AvailableTimeVariation(BaseModel):
    id: UUID = uuid4()
    category: Literal[OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS] = (
        OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS
    )
    description: str
    startTime: datetime
    endTime: datetime


class AvailableTimePublicHolidays(BaseModel):
    id: UUID = uuid4()
    category: Literal[OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS] = (
        OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS
    )
    startTime: time
    endTime: time


class NotAvailable(BaseModel):
    id: UUID = uuid4()
    category: Literal[OpeningTimeCategory.NOT_AVAILABLE] = (
        OpeningTimeCategory.NOT_AVAILABLE
    )
    description: str
    unavailableDate: date


OpeningTime = Annotated[
    Union[
        AvailableTime, AvailableTimeVariation, AvailableTimePublicHolidays, NotAvailable
    ],
    Field(discriminator="category"),
]


class HealthcareService(DBModel):
    identifier_oldDoS_uid: str
    active: bool
    category: str
    providedBy: UUID | None
    location: UUID | None
    name: str
    telecom: Telecom | None
    type: str
    openingTime: list[OpeningTime] | None

    @classmethod
    def from_dos(  # noqa: PLR0913
        cls,
        data: dict,
        existing_identifier: UUID | str | None = None,
        created_datetime: datetime | None = None,
        updated_datetime: datetime | None = None,
        organisation_id: UUID | str | None = None,
        location_id: UUID | str | None = None,
    ) -> "Organisation":
        """
        Create an HealthcareService instance from source DoS data.

        :param data: The source data dictionary from the 'services' DoS table.
        :param created_datetime: The datetime when the service was created.
        :param updated_datetime: The datetime when the service was last updated.
        :param organisation_id: The organisation managing the service.
        :return: An Service instance.
        """
        service_id = uuid4() or existing_identifier
        return HealthcareService(
            id=service_id,
            identifier_oldDoS_uid=data["uid"],
            active=True,
            category="unknown",  # TODO: in future ticket we will map type to category
            providedBy=organisation_id,
            location=location_id,
            name=data["name"],
            telecom=Telecom(
                phone_public=data["publicphone"],
                phone_private=data["nonpublicphone"],
                email=data["email"],
                web=data["web"],
            ),
            openingTime=HealthcareService.assign_opening_times(data["availability"]),
            type=data["type"],
            createdBy="ROBOT",
            createdDateTime=created_datetime or datetime.now(UTC),
            modifiedBy="ROBOT",
            modifiedDateTime=updated_datetime or datetime.now(UTC),
        )

    @classmethod
    def assign_opening_times(cls, availability: dict) -> OpeningTime:
        if availability is None:
            return None

        items = [
            AvailableTime(
                category=OpeningTimeCategory.AVAILABLE_TIME,
                dayOfWeek=data["dayOfWeek"][0],
                startTime=data["availableStartTime"],
                endTime=data["availableEndTime"],
            )
            for data in availability["availableTime"]
        ]

        if availability["availableTimePublicHolidays"] is not None:
            for data in availability["availableTimePublicHolidays"]:
                items.append(
                    AvailableTimePublicHolidays(
                        category=OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS,
                        startTime=data["availableStartTime"],
                        endTime=data["availableEndTime"],
                    )
                )

        if availability["availableTimeVariations"] is not None:
            for data in availability["availableTimeVariations"]:
                items.append(
                    AvailableTimeVariation(
                        category=OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS,
                        description=data["description"],
                        startTime=data["during"]["start"],
                        endTime=data["during"]["end"],
                    )
                )

        if availability["notAvailable"] is not None:
            for data in availability["notAvailable"]:
                items.append(
                    NotAvailable(
                        category=OpeningTimeCategory.NOT_AVAILABLE,
                        description=data["description"],
                        unavailableDate=data["start"],
                    )
                )

        return items if len(items) > 0 else None


payloadMimeType_mapping = {
    "PDF": "application/pdf",
    "HTML": "text/html",
    "FHIR": "application/fhir",
    "email": "message/rfc822",
    "telno": "text/vcard",
}


class Endpoint(DBModel):
    identifier_oldDoS_id: int | None
    status: str
    connectionType: str
    name: str | None
    payloadMimeType: str | None
    description: str
    payloadType: str | None
    address: str
    managedByOrganisation: UUID
    service: UUID | None
    order: int
    isCompressionEnabled: bool

    @classmethod
    def from_dos(
        cls,
        data: dict,
        created_datetime: datetime | None = None,
        updated_datetime: datetime | None = None,
        managed_by_id: UUID | None = None,
        service_id: UUID | None = None,
    ) -> "Endpoint":
        """
        Create an Endpoint instance from source DoS data.

        :param data: The source data dictionary from the 'serviceendpoints' DoS table.
        :param created_datetime: The datetime when the endpoint was created.
        :param updated_datetime: The datetime when the endpoint was last updated.
        :param managed_by_id: The ID of the managing organisation.
        :param service_id: The ID of the healthcare service.
        :return: An Endpoint instance.
        """
        payload_type = data["interaction"]

        payloadMimeType = payloadMimeType_mapping.get(data["format"], data["format"])

        if data["transport"] == "telno":
            payload_type = None
            payloadMimeType = None

        return Endpoint(
            id=uuid4(),
            identifier_oldDoS_id=data["id"],
            status="active",
            connectionType=data["transport"],
            name=None,
            description=data["businessscenario"],
            payloadType=payload_type,
            payloadMimeType=payloadMimeType,
            address=data["address"],
            managedByOrganisation=managed_by_id,
            service=service_id,
            order=data["endpointorder"],
            isCompressionEnabled=data["iscompressionenabled"] == "compressed",
            createdBy="ROBOT",
            createdDateTime=created_datetime or datetime.now(UTC),
            modifiedBy="ROBOT",
            modifiedDateTime=updated_datetime or datetime.now(UTC),
        )
