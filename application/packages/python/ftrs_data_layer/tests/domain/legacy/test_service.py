from datetime import date, time
from decimal import Decimal

from ftrs_data_layer.domain.legacy.base import LegacyDoSModel
from ftrs_data_layer.domain.legacy.service import (
    OpeningTimeDay,
    Service,
    ServiceAgeRange,
    ServiceDayOpening,
    ServiceDayOpeningTime,
    ServiceDisposition,
    ServiceEndpoint,
    ServiceSGSD,
    ServiceSpecifiedOpeningDate,
    ServiceSpecifiedOpeningTime,
    ServiceType,
)


class TestService:
    """Tests for Service legacy model."""

    def test_service_table_name(self) -> None:
        """Test that Service has correct table name."""
        assert Service.__tablename__ == "services"

    def test_service_inherits_legacy_dos_model(self) -> None:
        """Test that Service inherits from LegacyDoSModel."""
        assert issubclass(Service, LegacyDoSModel)

    def test_create_service_minimal(self) -> None:
        """Test creating Service with minimal required fields."""
        service = Service(
            id=1,
            uid="test-uid-001",
            name="Test GP Practice",
            openallhours=False,
            restricttoreferrals=False,
            typeid=1,
        )

        assert service.id == 1
        assert service.uid == "test-uid-001"
        assert service.name == "Test GP Practice"
        assert service.openallhours is False
        assert service.restricttoreferrals is False
        assert service.typeid == 1

    def test_create_service_full(self) -> None:
        """Test creating Service with all fields."""
        service = Service(
            id=2,
            uid="test-uid-002",
            name="Full Service Test",
            odscode="ABC123",
            isnational=False,
            openallhours=True,
            publicreferralinstructions="Walk-in available",
            telephonetriagereferralinstructions="Call first",
            restricttoreferrals=True,
            address="123 Test Street",
            town="Test Town",
            postcode="AB1 2CD",
            easting=123456,
            northing=654321,
            publicphone="01onal11 1234567",
            nonpublicphone="020 7654 3210",
            fax="020 7654 3211",
            email="test@example.com",
            web="https://www.example.com",
            createdby="admin",
            modifiedby="editor",
            typeid=2,
            parentid=1,
            subregionid=10,
            statusid=1,
            organisationid=100,
            returnifopenminutes=30,
            publicname="Public Service Name",
            latitude=Decimal("51.5074"),
            longitude=Decimal("-0.1278"),
            professionalreferralinfo="Referral info here",
        )

        assert service.odscode == "ABC123"
        assert service.address == "123 Test Street"
        assert service.latitude == Decimal("51.5074")

    def test_service_nullable_fields(self) -> None:
        """Test that optional fields can be None."""
        service = Service(
            id=3,
            uid="test-uid-003",
            name="Minimal Service",
            openallhours=False,
            restricttoreferrals=False,
            typeid=1,
        )

        assert service.odscode is None
        assert service.address is None
        assert service.latitude is None

    def test_service_has_relationships(self) -> None:
        """Test that Service has relationship attributes defined."""
        service = Service(
            id=4,
            uid="test-uid-004",
            name="Service with relationships",
            openallhours=False,
            restricttoreferrals=False,
            typeid=1,
        )

        assert hasattr(service, "endpoints")
        assert hasattr(service, "scheduled_opening_times")
        assert hasattr(service, "specified_opening_times")
        assert hasattr(service, "sgsds")
        assert hasattr(service, "dispositions")
        assert hasattr(service, "age_range")


class TestServiceType:
    """Tests for ServiceType legacy model."""

    def test_service_type_table_name(self) -> None:
        """Test that ServiceType has correct table name."""
        assert ServiceType.__tablename__ == "servicetypes"

    def test_create_service_type(self) -> None:
        """Test creating ServiceType instance."""
        service_type = ServiceType(
            id=1,
            name="GP Practice",
            nationalranking="1",
            searchcapacitystatus=True,
            capacitymodel="standard",
            capacityreset="daily",
        )

        assert service_type.id == 1
        assert service_type.name == "GP Practice"
        assert service_type.searchcapacitystatus is True


class TestServiceEndpoint:
    """Tests for ServiceEndpoint legacy model."""

    def test_service_endpoint_table_name(self) -> None:
        """Test that ServiceEndpoint has correct table name."""
        assert ServiceEndpoint.__tablename__ == "serviceendpoints"

    def test_create_service_endpoint(self) -> None:
        """Test creating ServiceEndpoint instance."""
        endpoint = ServiceEndpoint(
            id=1,
            endpointorder=1,
            transport="itk",
            format="CDA",
            interaction="Primary",
            businessscenario="Primary",
            address="https://example.com/endpoint",
            comment="Test endpoint",
            iscompressionenabled="Y",
            serviceid=100,
        )

        assert endpoint.id == 1
        assert endpoint.endpointorder == 1
        assert endpoint.transport == "itk"
        assert endpoint.serviceid == 100


class TestServiceDayOpening:
    """Tests for ServiceDayOpening legacy model."""

    def test_service_day_opening_table_name(self) -> None:
        """Test that ServiceDayOpening has correct table name."""
        assert ServiceDayOpening.__tablename__ == "servicedayopenings"

    def test_create_service_day_opening(self) -> None:
        """Test creating ServiceDayOpening instance."""
        day_opening = ServiceDayOpening(
            id=1,
            serviceid=100,
            dayid=1,
        )

        assert day_opening.id == 1
        assert day_opening.serviceid == 100
        assert day_opening.dayid == 1

    def test_service_day_opening_has_times_relationship(self) -> None:
        """Test that ServiceDayOpening has times relationship."""
        day_opening = ServiceDayOpening(id=2, serviceid=100, dayid=2)
        assert hasattr(day_opening, "times")


class TestServiceDayOpeningTime:
    """Tests for ServiceDayOpeningTime legacy model."""

    def test_service_day_opening_time_table_name(self) -> None:
        """Test that ServiceDayOpeningTime has correct table name."""
        assert ServiceDayOpeningTime.__tablename__ == "servicedayopeningtimes"

    def test_create_service_day_opening_time(self) -> None:
        """Test creating ServiceDayOpeningTime instance."""
        opening_time = ServiceDayOpeningTime(
            id=1,
            starttime=time(9, 0, 0),
            endtime=time(17, 0, 0),
            servicedayopeningid=1,
        )

        assert opening_time.id == 1
        assert opening_time.starttime == time(9, 0, 0)
        assert opening_time.endtime == time(17, 0, 0)


class TestServiceSpecifiedOpeningDate:
    """Tests for ServiceSpecifiedOpeningDate legacy model."""

    def test_specified_opening_date_table_name(self) -> None:
        """Test that ServiceSpecifiedOpeningDate has correct table name."""
        assert ServiceSpecifiedOpeningDate.__tablename__ == "servicespecifiedopeningdates"

    def test_create_specified_opening_date(self) -> None:
        """Test creating ServiceSpecifiedOpeningDate instance."""
        opening_date = ServiceSpecifiedOpeningDate(
            id=1,
            serviceid=100,
            date=date(2025, 12, 25),
        )

        assert opening_date.id == 1
        assert opening_date.serviceid == 100
        assert opening_date.date == date(2025, 12, 25)

    def test_specified_opening_date_has_times_relationship(self) -> None:
        """Test that ServiceSpecifiedOpeningDate has times relationship."""
        opening_date = ServiceSpecifiedOpeningDate(id=2, serviceid=100, date=date(2025, 1, 1))
        assert hasattr(opening_date, "times")


class TestServiceSpecifiedOpeningTime:
    """Tests for ServiceSpecifiedOpeningTime legacy model."""

    def test_specified_opening_time_table_name(self) -> None:
        """Test that ServiceSpecifiedOpeningTime has correct table name."""
        assert ServiceSpecifiedOpeningTime.__tablename__ == "servicespecifiedopeningtimes"

    def test_create_specified_opening_time(self) -> None:
        """Test creating ServiceSpecifiedOpeningTime instance."""
        opening_time = ServiceSpecifiedOpeningTime(
            id=1,
            starttime=time(10, 0, 0),
            endtime=time(14, 0, 0),
            isclosed=False,
            servicespecifiedopeningdateid=1,
        )

        assert opening_time.id == 1
        assert opening_time.starttime == time(10, 0, 0)
        assert opening_time.endtime == time(14, 0, 0)
        assert opening_time.isclosed is False


class TestOpeningTimeDay:
    """Tests for OpeningTimeDay legacy model."""

    def test_opening_time_day_table_name(self) -> None:
        """Test that OpeningTimeDay has correct table name."""
        assert OpeningTimeDay.__tablename__ == "openingtimedays"

    def test_create_opening_time_day(self) -> None:
        """Test creating OpeningTimeDay instance."""
        day = OpeningTimeDay(id=1, name="Monday")

        assert day.id == 1
        assert day.name == "Monday"


class TestServiceSGSD:
    """Tests for ServiceSGSD legacy model."""

    def test_service_sgsd_table_name(self) -> None:
        """Test that ServiceSGSD has correct table name."""
        assert ServiceSGSD.__tablename__ == "servicesgsds"

    def test_create_service_sgsd(self) -> None:
        """Test creating ServiceSGSD instance."""
        sgsd = ServiceSGSD(
            id=1,
            serviceid=100,
            sgid=1000,
            sdid=4003,
        )

        assert sgsd.id == 1
        assert sgsd.serviceid == 100
        assert sgsd.sgid == 1000
        assert sgsd.sdid == 4003


class TestServiceDisposition:
    """Tests for ServiceDisposition legacy model."""

    def test_service_disposition_table_name(self) -> None:
        """Test that ServiceDisposition has correct table name."""
        assert ServiceDisposition.__tablename__ == "servicedispositions"

    def test_create_service_disposition(self) -> None:
        """Test creating ServiceDisposition instance."""
        disposition = ServiceDisposition(
            id=1,
            serviceid=100,
            dispositionid=114,
        )

        assert disposition.id == 1
        assert disposition.serviceid == 100
        assert disposition.dispositionid == 114


class TestServiceAgeRange:
    """Tests for ServiceAgeRange legacy model."""

    def test_service_age_range_table_name(self) -> None:
        """Test that ServiceAgeRange has correct table name."""
        assert ServiceAgeRange.__tablename__ == "serviceagerange"

    def test_create_service_age_range(self) -> None:
        """Test creating ServiceAgeRange instance."""
        age_range = ServiceAgeRange(
            id=1,
            serviceid=100,
            daysfrom=Decimal("0"),
            daysto=Decimal("36500"),
        )

        assert age_range.id == 1
        assert age_range.serviceid == 100
        assert age_range.daysfrom == Decimal("0")
        assert age_range.daysto == Decimal("36500")
