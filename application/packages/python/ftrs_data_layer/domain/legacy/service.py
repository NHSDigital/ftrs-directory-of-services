from datetime import date, datetime, time
from decimal import Decimal

from ftrs_data_layer.domain.legacy.base import LegacyDoSModel
from sqlmodel import Field, Relationship


class Service(LegacyDoSModel, table=True):
    __tablename__ = "services"

    id: int = Field(primary_key=True)
    uid: str = Field(index=True, unique=True)
    name: str
    odscode: str | None
    isnational: bool | None
    openallhours: bool
    publicreferralinstructions: str | None
    telephonetriagereferralinstructions: str | None
    restricttoreferrals: bool
    address: str | None
    town: str | None
    postcode: str | None
    easting: int | None
    northing: int | None
    publicphone: str | None
    nonpublicphone: str | None
    fax: str | None
    email: str | None
    web: str | None
    createdby: str | None
    createdtime: datetime | None
    modifiedby: str | None
    modifiedtime: datetime | None
    lasttemplatename: str | None
    lasttemplateid: int | None
    typeid: int
    parentid: int | None
    subregionid: int | None
    statusid: int | None
    organisationid: int | None
    returnifopenminutes: int | None
    publicname: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    professionalreferralinfo: str | None
    lastverified: str | None
    nextverificationdue: str | None

    endpoints: list["ServiceEndpoint"] = Relationship()
    scheduled_opening_times: list["ServiceDayOpening"] = Relationship()
    specified_opening_times: list["ServiceSpecifiedOpeningDate"] = Relationship()
    sgsds: list["ServiceSGSD"] = Relationship()
    dispositions: list["ServiceDisposition"] = Relationship()
    age_range: list["ServiceAgeRange"] = Relationship()


class ServiceType(LegacyDoSModel, table=True):
    __tablename__ = "servicetypes"

    id: int = Field(primary_key=True)
    name: str
    nationalranking: str | None
    searchcapacitystatus: bool | None
    capacitymodel: str | None
    capacityreset: str | None


class ServiceEndpoint(LegacyDoSModel, table=True):
    __tablename__ = "serviceendpoints"

    id: int = Field(primary_key=True)
    endpointorder: int
    transport: str | None
    format: str | None
    interaction: str | None
    businessscenario: str | None
    address: str | None
    comment: str | None
    iscompressionenabled: str | None
    serviceid: int = Field(foreign_key="services.id")


class ServiceDayOpeningTime(LegacyDoSModel, table=True):
    __tablename__ = "servicedayopeningtimes"

    id: int = Field(primary_key=True)
    starttime: time
    endtime: time
    servicedayopeningid: int = Field(foreign_key="servicedayopenings.id")


class ServiceSpecifiedOpeningDate(LegacyDoSModel, table=True):
    __tablename__ = "servicespecifiedopeningdates"

    id: int = Field(primary_key=True)
    serviceid: int = Field(foreign_key="services.id")
    date: date
    times: list["ServiceSpecifiedOpeningTime"] = Relationship()


class ServiceSpecifiedOpeningTime(LegacyDoSModel, table=True):
    __tablename__ = "servicespecifiedopeningtimes"

    id: int = Field(primary_key=True)
    starttime: time
    endtime: time
    isclosed: bool
    servicespecifiedopeningdateid: int = Field(
        foreign_key="servicespecifiedopeningdates.id"
    )


class OpeningTimeDay(LegacyDoSModel, table=True):
    __tablename__ = "openingtimedays"

    id: int = Field(primary_key=True)
    name: str


class ServiceDayOpening(LegacyDoSModel, table=True):
    __tablename__ = "servicedayopenings"

    id: int = Field(primary_key=True)
    serviceid: int = Field(foreign_key="services.id")
    dayid: int
    times: list["ServiceDayOpeningTime"] = Relationship()


class ServiceSGSD(LegacyDoSModel, table=True):
    __tablename__ = "servicesgsds"

    id: int = Field(primary_key=True)
    serviceid: int = Field(foreign_key="services.id")
    sdid: int
    sgid: int


class ServiceDisposition(LegacyDoSModel, table=True):
    __tablename__ = "servicedispositions"

    id: int = Field(primary_key=True)
    serviceid: int = Field(foreign_key="services.id")
    dispositionid: int = Field(foreign_key="dispositions.id")


class ServiceAgeRange(LegacyDoSModel, table=True):
    __tablename__ = "serviceagerange"

    id: int = Field(primary_key=True)
    serviceid: int = Field(foreign_key="services.id")
    daysfrom: Decimal
    daysto: Decimal
