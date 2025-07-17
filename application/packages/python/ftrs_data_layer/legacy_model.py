from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import MetaData, Column, Enum as EnumType, INTEGER
from enum import IntEnum
from decimal import Decimal
from datetime import time, date, datetime


class LegacyDoSModel(SQLModel):
    metadata = MetaData(schema="pathwaysdos")


class ServiceTypeEnum(IntEnum):
    LOCAL_TEMPLATE = -2
    DOS_REGION = -1
    THERAPY = 4
    COMMISSIONING_CLUSTER = 6
    MENTAL_HEALTH = 7
    SOCIAL_CARE = 8
    VOLUNTARY = 11
    DENTAL_PRACTICE = 12
    PHARMACY = 13
    OPTICAL = 14
    CLINIC = 17
    HEALTH_VISITOR = 18
    MIDWIFERY = 19
    COMMUNITY_BASED = 20
    RETIRED = 21
    COMMISSIONING_ORGANISATION = 22
    CARE_HOME = 24
    IUC_TREATMENT = 25
    INTERMEDIATE_CARE = 27
    COMMUNITY_HOSPITAL = 28
    SEXUAL_HEALTH = 29
    COMMUNITY_DISTRICT_NURSING = 38
    ED_CATCH_ALL = 40
    HOSPITAL_AAU = 41
    URGENT_CARE = 46
    DENTAL_EMERGENCY = 47
    SPECIALIST = 48
    PALLIATIVE_CARE = 50
    GP_PRACTICE = 100
    EMERGENCY_DEPARTMENT = 105
    CAPACITY_CRITICAL_CARE = 107
    CAPACITY_PICU = 108
    CAPACITY_BURNS = 109
    CAPACITY_MATERNITY = 110
    CAPACITY_PEDIATRIC = 111
    OPTICAL_ENHANCED = 112
    HEALTH_INFORMATION = 113
    CAPACITY_ACUTE_HOSPITAL = 114
    CAPACITY_RAG = 115
    ED_EYE_CASUALTY = 120
    PPCI = 121
    HASU = 112
    SAFEGUARDING = 129
    IUC_111_CALL_HANDLING = 130
    PHARMACY_URGENT_MEDICINES = 131
    PHARMACY_ENHANCED = 132
    IUC_CLINICAL_ASSESSMENT = 133
    PHARMACY_DISTANCE_SELLING = 134
    UTC = 135
    GP_ACCESS_HUB = 136
    IUC_PHARMACY_CLINICAL_ASSESSMENT = 137
    EMERGENCY_NATIONAL_RESPONSE = 138
    IUC_VALIDATION = 139
    SDEC = 140
    HOSPITAL_STREAMING = 141
    MENTAL_HEALTH_CRISIS = 142
    SARC = 143
    IUC_DENTAL_CLINICAL_ASSESSMENT = 144
    IUC_PAEDIATRIC_CLINICAL_ASSESSMENT = 145
    URGENT_COMMUNITY_RESPONSE = 146
    COVID_MEDICINES_DELIVERY_UNIT = 147
    PHARMACY_BLOOD_PRESSURE_CHECK = 148
    PHARMACY_CONTRACEPTION = 149
    UTC_COLOCATED_ED = 150
    PRIMARY_CARE_NETWORK = 151
    PRIMARY_CARE_NETWORK_ENHANCED = 152
    MATERNITY_NEONATAL = 153
    EARLY_PREGNANCY_ASSESSMENT_UNIT = 154
    VIRTUAL_WARD = 155
    DENTAL_URGENT_CARE = 156
    INFECTION_HUB = 157
    AMBULANCE_SERVICE_PATHWAY = 158
    PRIMARY_CARE_CLINIC = 159
    CARE_TRANSFER_HUB = 160


class ServiceStatusEnum(IntEnum):
    ACTIVE = 1
    CLOSED = 2
    COMMISSIONING = 3
    PENDING = 4
    SUSPENDED = 5
    RETIRED = 6
    TEMPLATE = 7


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
    typeid: int = Field(foreign_key="servicetypes.id")
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

    type: "ServiceType" = Relationship()
    endpoints: list["ServiceEndpoint"] = Relationship()
    scheduled_opening_times: list["ServiceDayOpening"] = Relationship()
    specified_opening_times: list["ServiceSpecifiedOpeningDate"] = Relationship()


class OpeningTimeDay(LegacyDoSModel, table=True):
    __tablename__ = "openingtimedays"

    id: int = Field(primary_key=True)
    name: str


class ServiceDayOpening(LegacyDoSModel, table=True):
    __tablename__ = "servicedayopenings"

    id: int = Field(primary_key=True)
    serviceid: int = Field(foreign_key="services.id")
    dayid: int = Field(foreign_key="openingtimedays.id")
    day: OpeningTimeDay = Relationship()
    times: list["ServiceDayOpeningTime"] = Relationship()


class ServiceDayOpeningTime(LegacyDoSModel, table=True):
    __tablename__ = "servicedayopeningtimes"

    id: int = Field(primary_key=True)
    starttime: time
    endtime: time
    servicedayopeningid: int = Field(foreign_key="servicedayopenings.id")


class ServiceType(LegacyDoSModel, table=True):
    __tablename__ = "servicetypes"

    id: int = Field(primary_key=True)
    name: str
    nationalranking: str | None
    searchcapacitystatus: bool | None
    capacitymodel: str | None
    capacityreset: str | None


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
    iscompressionenabled: bool | None
    serviceid: int = Field(foreign_key="services.id")
