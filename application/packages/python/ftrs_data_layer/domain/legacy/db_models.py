import datetime as dt
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class LegacyDoSModel(DeclarativeBase):
    metadata = MetaData(schema="pathwaysdos")


class Service(LegacyDoSModel):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, index=True, unique=True)
    name: Mapped[str] = mapped_column(String)
    odscode: Mapped[str | None] = mapped_column(String, nullable=True)
    isnational: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    openallhours: Mapped[bool] = mapped_column(Boolean)
    publicreferralinstructions: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    telephonetriagereferralinstructions: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    restricttoreferrals: Mapped[bool] = mapped_column(Boolean)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    town: Mapped[str | None] = mapped_column(String, nullable=True)
    postcode: Mapped[str | None] = mapped_column(String, nullable=True)
    easting: Mapped[int | None] = mapped_column(Integer, nullable=True)
    northing: Mapped[int | None] = mapped_column(Integer, nullable=True)
    publicphone: Mapped[str | None] = mapped_column(String, nullable=True)
    nonpublicphone: Mapped[str | None] = mapped_column(String, nullable=True)
    fax: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    web: Mapped[str | None] = mapped_column(String, nullable=True)
    createdby: Mapped[str | None] = mapped_column(String, nullable=True)
    createdtime: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    modifiedby: Mapped[str | None] = mapped_column(String, nullable=True)
    modifiedtime: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    lasttemplatename: Mapped[str | None] = mapped_column(String, nullable=True)
    lasttemplateid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    typeid: Mapped[int] = mapped_column(Integer)
    parentid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subregionid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    statusid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    organisationid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    returnifopenminutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    publicname: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    professionalreferralinfo: Mapped[str | None] = mapped_column(String, nullable=True)
    lastverified: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    nextverificationdue: Mapped[dt.datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    endpoints: Mapped[list["ServiceEndpoint"]] = relationship(back_populates="service")
    scheduled_opening_times: Mapped[list["ServiceDayOpening"]] = relationship(
        back_populates="service"
    )
    specified_opening_times: Mapped[list["ServiceSpecifiedOpeningDate"]] = relationship(
        back_populates="service"
    )
    sgsds: Mapped[list["ServiceSGSD"]] = relationship(back_populates="service")
    dispositions: Mapped[list["ServiceDisposition"]] = relationship(
        back_populates="service"
    )
    age_range: Mapped[list["ServiceAgeRange"]] = relationship(back_populates="service")


class ServiceType(LegacyDoSModel):
    __tablename__ = "servicetypes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    nationalranking: Mapped[str | None] = mapped_column(String, nullable=True)
    searchcapacitystatus: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    capacitymodel: Mapped[str | None] = mapped_column(String, nullable=True)
    capacityreset: Mapped[str | None] = mapped_column(String, nullable=True)


class ServiceEndpoint(LegacyDoSModel):
    __tablename__ = "serviceendpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    endpointorder: Mapped[int] = mapped_column(Integer)
    transport: Mapped[str | None] = mapped_column(String, nullable=True)
    format: Mapped[str | None] = mapped_column(String, nullable=True)
    interaction: Mapped[str | None] = mapped_column(String, nullable=True)
    businessscenario: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    iscompressionenabled: Mapped[str | None] = mapped_column(String, nullable=True)
    serviceid: Mapped[int] = mapped_column(Integer, ForeignKey("services.id"))

    service: Mapped["Service"] = relationship(back_populates="endpoints")


class ServiceDayOpeningTime(LegacyDoSModel):
    __tablename__ = "servicedayopeningtimes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    starttime: Mapped[dt.time] = mapped_column(Time)
    endtime: Mapped[dt.time] = mapped_column(Time)
    servicedayopeningid: Mapped[int] = mapped_column(
        Integer, ForeignKey("servicedayopenings.id")
    )

    servicedayopening: Mapped["ServiceDayOpening"] = relationship(
        back_populates="times"
    )


class ServiceSpecifiedOpeningDate(LegacyDoSModel):
    __tablename__ = "servicespecifiedopeningdates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    serviceid: Mapped[int] = mapped_column(Integer, ForeignKey("services.id"))
    date: Mapped[dt.date] = mapped_column(Date)

    service: Mapped["Service"] = relationship(back_populates="specified_opening_times")
    times: Mapped[list["ServiceSpecifiedOpeningTime"]] = relationship(
        back_populates="servicespecifiedopeningdate"
    )


class ServiceSpecifiedOpeningTime(LegacyDoSModel):
    __tablename__ = "servicespecifiedopeningtimes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    starttime: Mapped[dt.time] = mapped_column(Time)
    endtime: Mapped[dt.time] = mapped_column(Time)
    isclosed: Mapped[bool] = mapped_column(Boolean)
    servicespecifiedopeningdateid: Mapped[int] = mapped_column(
        Integer, ForeignKey("servicespecifiedopeningdates.id")
    )

    servicespecifiedopeningdate: Mapped["ServiceSpecifiedOpeningDate"] = relationship(
        back_populates="times"
    )


class OpeningTimeDay(LegacyDoSModel):
    __tablename__ = "openingtimedays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)


class ServiceDayOpening(LegacyDoSModel):
    __tablename__ = "servicedayopenings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    serviceid: Mapped[int] = mapped_column(Integer, ForeignKey("services.id"))
    dayid: Mapped[int] = mapped_column(Integer)

    service: Mapped["Service"] = relationship(back_populates="scheduled_opening_times")
    times: Mapped[list["ServiceDayOpeningTime"]] = relationship(
        back_populates="servicedayopening"
    )


class ServiceSGSD(LegacyDoSModel):
    __tablename__ = "servicesgsds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    serviceid: Mapped[int] = mapped_column(Integer, ForeignKey("services.id"))
    sdid: Mapped[int] = mapped_column(Integer)
    sgid: Mapped[int] = mapped_column(Integer)

    service: Mapped["Service"] = relationship(back_populates="sgsds")


class ServiceDisposition(LegacyDoSModel):
    __tablename__ = "servicedispositions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    serviceid: Mapped[int] = mapped_column(Integer, ForeignKey("services.id"))
    dispositionid: Mapped[int] = mapped_column(Integer, ForeignKey("dispositions.id"))

    service: Mapped["Service"] = relationship(back_populates="dispositions")
    disposition: Mapped["Disposition"] = relationship()


class ServiceAgeRange(LegacyDoSModel):
    __tablename__ = "serviceagerange"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    serviceid: Mapped[int] = mapped_column(Integer, ForeignKey("services.id"))
    daysfrom: Mapped[Decimal] = mapped_column(Numeric)
    daysto: Mapped[Decimal] = mapped_column(Numeric)

    service: Mapped["Service"] = relationship(back_populates="age_range")


class SymptomGroup(LegacyDoSModel):
    __tablename__ = "symptomgroups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    zcodeexists: Mapped[bool | None] = mapped_column(Boolean, nullable=True)


class SymptomDiscriminator(LegacyDoSModel):
    __tablename__ = "symptomdiscriminators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    synonyms: Mapped[list["SymptomDiscriminatorSynonym"]] = relationship(
        back_populates="symptomdiscriminator"
    )


class SymptomDiscriminatorSynonym(LegacyDoSModel):
    __tablename__ = "symptomdiscriminatorsynonyms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    symptomdiscriminatorid: Mapped[int] = mapped_column(
        Integer, ForeignKey("symptomdiscriminators.id")
    )

    symptomdiscriminator: Mapped["SymptomDiscriminator"] = relationship(
        back_populates="synonyms"
    )


class SymptomGroupSymptomDiscriminator(LegacyDoSModel):
    __tablename__ = "symptomgroupsymptomdiscriminators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symptomgroupid: Mapped[int] = mapped_column(Integer, ForeignKey("symptomgroups.id"))
    symptomdiscriminatorid: Mapped[int] = mapped_column(
        Integer, ForeignKey("symptomdiscriminators.id")
    )

    symptomgroup: Mapped["SymptomGroup"] = relationship()
    symptomdiscriminator: Mapped["SymptomDiscriminator"] = relationship()


class Disposition(LegacyDoSModel):
    __tablename__ = "dispositions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    dxcode: Mapped[str | None] = mapped_column(String, nullable=True)
    dispositiontime: Mapped[int | None] = mapped_column(Integer, nullable=True)
