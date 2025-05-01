from datetime import UTC, datetime
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


class Location(DBModel):
    active: bool
    address_street: str
    address_postcode: str
    address_town: str
    managingOrganisation: UUID
    name: str | None = None
    positionGCS_latitude: float
    positionGCS_longitude: float
    positionGCS_easting: float
    positionGCS_northing: float
    positionReferenceNumber_UPRN: int | None = None
    positionReferenceNumber_UBRN: int | None = None
    primaryAddress: bool
    partOf: UUID | None

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
            address={
                "street": data["address"],
                "town": data["town"],
                "postcode": data["postcode"],
            },
            name=None,
            positionGCS={"latitude": data["latitude"], "longitude": data["longitude"]},
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


class HealthcareService(DBModel):
    identifier_oldDoS_uid: str
    active: bool
    category: str
    providedBy: UUID | None
    location: UUID | None
    name: str
    telecom: Telecom | None
    type: str

    @classmethod
    def from_dos(
        cls,
        data: dict,
        existing_identifier: UUID | str | None = None,
        created_datetime: datetime | None = None,
        updated_datetime: datetime | None = None,
        organisation_id: UUID | str | None = None,
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
            location=None,
            name=data["name"],
            telecom=Telecom(
                phone_public=data["publicphone"],
                phone_private=data["nonpublicphone"],
                email=data["email"],
                web=data["web"],
            ),
            type=data["type"],
            createdBy="ROBOT",
            createdDateTime=created_datetime or datetime.now(UTC),
            modifiedBy="ROBOT",
            modifiedDateTime=updated_datetime or datetime.now(UTC),
        )


class Endpoint(DBModel):
    identifier_oldDoS_id: int | None
    status: str
    connectionType: str
    name: str | None
    format: str | None
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
        format = data["format"]

        if data["transport"] == "telno":
            payload_type = None
            format = None

        return Endpoint(
            id=uuid4(),
            identifier_oldDoS_id=data["id"],
            status="active",
            connectionType=data["transport"],
            name=None,
            description=data["businessscenario"],
            payloadType=payload_type,
            format=format,
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
