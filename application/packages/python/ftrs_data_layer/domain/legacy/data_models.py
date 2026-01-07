import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LegacyDoSDataModel(BaseModel):
    """Base Pydantic model for legacy DoS data models."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class ServiceDayOpeningTimeData(LegacyDoSDataModel):
    id: int
    starttime: dt.time
    endtime: dt.time
    servicedayopeningid: int


class ServiceDayOpeningData(LegacyDoSDataModel):
    id: int
    serviceid: int
    dayid: int
    times: list[ServiceDayOpeningTimeData] = []


class ServiceSpecifiedOpeningTimeData(LegacyDoSDataModel):
    id: int
    starttime: dt.time
    endtime: dt.time
    isclosed: bool
    servicespecifiedopeningdateid: int


class ServiceSpecifiedOpeningDateData(LegacyDoSDataModel):
    id: int
    serviceid: int
    date: dt.date
    times: list[ServiceSpecifiedOpeningTimeData] = []


class ServiceEndpointData(LegacyDoSDataModel):
    id: int
    endpointorder: int
    transport: str | None = None
    format: str | None = None
    interaction: str | None = None
    businessscenario: str | None = None
    address: str | None = None
    comment: str | None = None
    iscompressionenabled: str | None = None
    serviceid: int


class ServiceSGSDData(LegacyDoSDataModel):
    id: int
    serviceid: int
    sdid: int
    sgid: int


class DispositionData(LegacyDoSDataModel):
    id: int
    name: str
    dxcode: str | None = None
    dispositiontime: int | None = None


class ServiceDispositionData(LegacyDoSDataModel):
    id: int
    serviceid: int
    dispositionid: int


class ServiceAgeRangeData(LegacyDoSDataModel):
    id: int
    serviceid: int
    daysfrom: Decimal
    daysto: Decimal


class ServiceTypeData(LegacyDoSDataModel):
    id: int
    name: str
    nationalranking: str | None = None
    searchcapacitystatus: bool | None = None
    capacitymodel: str | None = None
    capacityreset: str | None = None


class OpeningTimeDayData(LegacyDoSDataModel):
    id: int
    name: str


class ServiceData(LegacyDoSDataModel):
    id: int
    uid: str
    name: str
    odscode: str | None = None
    isnational: bool | None = None
    openallhours: bool
    publicreferralinstructions: str | None = None
    telephonetriagereferralinstructions: str | None = None
    restricttoreferrals: bool
    address: str | None = None
    town: str | None = None
    postcode: str | None = None
    easting: int | None = None
    northing: int | None = None
    publicphone: str | None = None
    nonpublicphone: str | None = None
    fax: str | None = None
    email: str | None = None
    web: str | None = None
    createdby: str | None = None
    createdtime: dt.datetime | None = None
    modifiedby: str | None = None
    modifiedtime: dt.datetime | None = None
    lasttemplatename: str | None = None
    lasttemplateid: int | None = None
    typeid: int
    parentid: int | None = None
    subregionid: int | None = None
    statusid: int | None = None
    organisationid: int | None = None
    returnifopenminutes: int | None = None
    publicname: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    professionalreferralinfo: str | None = None
    lastverified: dt.datetime | None = None
    nextverificationdue: dt.datetime | None = None

    endpoints: list[ServiceEndpointData] = Field(default_factory=list)
    scheduled_opening_times: list[ServiceDayOpeningData] = Field(default_factory=list)
    specified_opening_times: list[ServiceSpecifiedOpeningDateData] = Field(
        default_factory=list
    )
    sgsds: list[ServiceSGSDData] = Field(default_factory=list)
    dispositions: list[ServiceDispositionData] = Field(default_factory=list)
    age_range: list[ServiceAgeRangeData] = Field(default_factory=list)


class SymptomGroupData(LegacyDoSDataModel):
    id: int
    name: str
    zcodeexists: bool | None = None


class SymptomDiscriminatorSynonymData(LegacyDoSDataModel):
    id: int
    name: str | None = None
    symptomdiscriminatorid: int


class SymptomDiscriminatorData(LegacyDoSDataModel):
    id: int
    description: str | None = None
    synonyms: list[SymptomDiscriminatorSynonymData] = []


class SymptomGroupSymptomDiscriminatorData(LegacyDoSDataModel):
    id: int
    symptomgroupid: int
    symptomdiscriminatorid: int
