from ftrs_data_layer.domain.enums import (
    ClinicalCodeSource,
    ClinicalCodeType,
    DayOfWeek,
    EndpointBusinessScenario,
    EndpointConnectionType,
    EndpointPayloadMimeType,
    EndpointPayloadType,
    EndpointStatus,
    HealthcareServiceCategory,
    HealthcareServiceType,
    OpeningTimeCategory,
    OrganisationType,
    OrganisationTypeCode,
    TelecomType,
    TimeUnit,
)


class TestOpeningTimeCategory:
    """Tests for OpeningTimeCategory enum."""

    def test_available_time_value(self) -> None:
        """Test AVAILABLE_TIME value."""
        assert OpeningTimeCategory.AVAILABLE_TIME == "availableTime"
        assert OpeningTimeCategory.AVAILABLE_TIME.value == "availableTime"

    def test_available_time_variations_value(self) -> None:
        """Test AVAILABLE_TIME_VARIATIONS value."""
        assert OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS == "availableTimeVariations"

    def test_available_time_public_holidays_value(self) -> None:
        """Test AVAILABLE_TIME_PUBLIC_HOLIDAYS value."""
        assert OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS == "availableTimePublicHolidays"

    def test_not_available_value(self) -> None:
        """Test NOT_AVAILABLE value."""
        assert OpeningTimeCategory.NOT_AVAILABLE == "notAvailable"

    def test_opening_time_category_members(self) -> None:
        """Test that OpeningTimeCategory has exactly 4 members."""
        members = list(OpeningTimeCategory)
        assert len(members) == 4


class TestDayOfWeek:
    """Tests for DayOfWeek enum."""

    def test_day_values(self) -> None:
        """Test all day values."""
        assert DayOfWeek.MONDAY == "mon"
        assert DayOfWeek.TUESDAY == "tue"
        assert DayOfWeek.WEDNESDAY == "wed"
        assert DayOfWeek.THURSDAY == "thu"
        assert DayOfWeek.FRIDAY == "fri"
        assert DayOfWeek.SATURDAY == "sat"
        assert DayOfWeek.SUNDAY == "sun"

    def test_day_of_week_members(self) -> None:
        """Test that DayOfWeek has exactly 7 members."""
        members = list(DayOfWeek)
        assert len(members) == 7

    def test_day_of_week_is_string_enum(self) -> None:
        """Test that DayOfWeek values work as strings."""
        assert DayOfWeek.MONDAY.value == "mon"
        assert DayOfWeek.FRIDAY.value == "fri"


class TestOrganisationType:
    """Tests for OrganisationType enum."""

    def test_gp_practice_value(self) -> None:
        """Test GP_PRACTICE value."""
        assert OrganisationType.GP_PRACTICE == "GP Practice"
        assert OrganisationType.GP_PRACTICE.value == "GP Practice"

    def test_organisation_type_members(self) -> None:
        """Test that OrganisationType has at least 1 member."""
        members = list(OrganisationType)
        assert len(members) >= 1


class TestOrganisationTypeCode:
    """Tests for OrganisationTypeCode enum."""

    def test_prescribing_cost_centre_code(self) -> None:
        """Test PRESCRIBING_COST_CENTRE_CODE value."""
        assert OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE == "RO177"

    def test_gp_practice_role_code(self) -> None:
        """Test GP_PRACTICE_ROLE_CODE value."""
        assert OrganisationTypeCode.GP_PRACTICE_ROLE_CODE == "RO76"

    def test_out_of_hours_role_code(self) -> None:
        """Test OUT_OF_HOURS_ROLE_CODE value."""
        assert OrganisationTypeCode.OUT_OF_HOURS_ROLE_CODE == "RO80"

    def test_walk_in_centre_role_code(self) -> None:
        """Test WALK_IN_CENTRE_ROLE_CODE value."""
        assert OrganisationTypeCode.WALK_IN_CENTRE_ROLE_CODE == "RO87"

    def test_pharmacy_role_code(self) -> None:
        """Test PHARMACY_ROLE_CODE value."""
        assert OrganisationTypeCode.PHARMACY_ROLE_CODE == "RO182"

    def test_organisation_type_code_members(self) -> None:
        """Test that OrganisationTypeCode has exactly 5 members."""
        members = list(OrganisationTypeCode)
        assert len(members) == 5


class TestHealthcareServiceCategory:
    """Tests for HealthcareServiceCategory enum."""

    def test_gp_services_value(self) -> None:
        """Test GP_SERVICES value."""
        assert HealthcareServiceCategory.GP_SERVICES == "GP Services"


class TestHealthcareServiceType:
    """Tests for HealthcareServiceType enum."""

    def test_gp_consultation_service_value(self) -> None:
        """Test GP_CONSULTATION_SERVICE value."""
        assert HealthcareServiceType.GP_CONSULTATION_SERVICE == "GP Consultation Service"

    def test_pcn_service_value(self) -> None:
        """Test PCN_SERVICE value."""
        assert HealthcareServiceType.PCN_SERVICE == "Primary Care Network Enhanced Access Service"

    def test_healthcare_service_type_members(self) -> None:
        """Test that HealthcareServiceType has exactly 2 members."""
        members = list(HealthcareServiceType)
        assert len(members) == 2


class TestEndpointStatus:
    """Tests for EndpointStatus enum."""

    def test_active_value(self) -> None:
        """Test ACTIVE value."""
        assert EndpointStatus.ACTIVE == "active"

    def test_off_value(self) -> None:
        """Test OFF value."""
        assert EndpointStatus.OFF == "off"

    def test_endpoint_status_members(self) -> None:
        """Test that EndpointStatus has exactly 2 members."""
        members = list(EndpointStatus)
        assert len(members) == 2


class TestEndpointConnectionType:
    """Tests for EndpointConnectionType enum."""

    def test_itk_value(self) -> None:
        """Test ITK value."""
        assert EndpointConnectionType.ITK == "itk"

    def test_email_value(self) -> None:
        """Test EMAIL value."""
        assert EndpointConnectionType.EMAIL == "email"

    def test_telno_value(self) -> None:
        """Test TELNO value."""
        assert EndpointConnectionType.TELNO == "telno"

    def test_http_value(self) -> None:
        """Test HTTP value."""
        assert EndpointConnectionType.HTTP == "http"

    def test_endpoint_connection_type_members(self) -> None:
        """Test that EndpointConnectionType has exactly 4 members."""
        members = list(EndpointConnectionType)
        assert len(members) == 4


class TestEndpointBusinessScenario:
    """Tests for EndpointBusinessScenario enum."""

    def test_primary_value(self) -> None:
        """Test PRIMARY value."""
        assert EndpointBusinessScenario.PRIMARY == "Primary"

    def test_copy_value(self) -> None:
        """Test COPY value."""
        assert EndpointBusinessScenario.COPY == "Copy"

    def test_endpoint_business_scenario_members(self) -> None:
        """Test that EndpointBusinessScenario has exactly 2 members."""
        members = list(EndpointBusinessScenario)
        assert len(members) == 2


class TestEndpointPayloadType:
    """Tests for EndpointPayloadType enum."""

    def test_ed_value(self) -> None:
        """Test ED value."""
        assert EndpointPayloadType.ED == "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0"

    def test_gp_primary_value(self) -> None:
        """Test GP_PRIMARY value."""
        assert EndpointPayloadType.GP_PRIMARY == "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0"

    def test_gp_copy_value(self) -> None:
        """Test GP_COPY value."""
        assert EndpointPayloadType.GP_COPY == "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0"

    def test_other_value(self) -> None:
        """Test OTHER value."""
        assert EndpointPayloadType.OTHER == "urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0"

    def test_ambulance_value(self) -> None:
        """Test AMBULANCE value."""
        assert EndpointPayloadType.AMBULANCE == "urn:nhs-itk:interaction:primaryNHS111RequestforAmbulance-v2-0"

    def test_scheduling_value(self) -> None:
        """Test SCHEDULING value."""
        assert EndpointPayloadType.SCHEDULING == "scheduling"

    def test_endpoint_payload_type_members(self) -> None:
        """Test that EndpointPayloadType has exactly 6 members."""
        members = list(EndpointPayloadType)
        assert len(members) == 6


class TestEndpointPayloadMimeType:
    """Tests for EndpointPayloadMimeType enum."""

    def test_pdf_value(self) -> None:
        """Test PDF value."""
        assert EndpointPayloadMimeType.PDF == "application/pdf"

    def test_html_value(self) -> None:
        """Test HTML value."""
        assert EndpointPayloadMimeType.HTML == "text/html"

    def test_fhir_value(self) -> None:
        """Test FHIR value."""
        assert EndpointPayloadMimeType.FHIR == "application/fhir"

    def test_xml_value(self) -> None:
        """Test XML value."""
        assert EndpointPayloadMimeType.XML == "xml"

    def test_email_value(self) -> None:
        """Test EMAIL value."""
        assert EndpointPayloadMimeType.EMAIL == "message/rfc822"

    def test_telno_value(self) -> None:
        """Test TELNO value."""
        assert EndpointPayloadMimeType.TELNO == "text/vcard"

    def test_cda_value(self) -> None:
        """Test CDA value."""
        assert EndpointPayloadMimeType.CDA == "application/hl7-cda+xml"

    def test_endpoint_payload_mime_type_members(self) -> None:
        """Test that EndpointPayloadMimeType has exactly 7 members."""
        members = list(EndpointPayloadMimeType)
        assert len(members) == 7


class TestClinicalCodeSource:
    """Tests for ClinicalCodeSource enum."""

    def test_pathways_value(self) -> None:
        """Test PATHWAYS value."""
        assert ClinicalCodeSource.PATHWAYS == "pathways"

    def test_service_finder_value(self) -> None:
        """Test SERVICE_FINDER value."""
        assert ClinicalCodeSource.SERVICE_FINDER == "servicefinder"

    def test_clinical_code_source_members(self) -> None:
        """Test that ClinicalCodeSource has exactly 2 members."""
        members = list(ClinicalCodeSource)
        assert len(members) == 2


class TestClinicalCodeType:
    """Tests for ClinicalCodeType enum."""

    def test_symptom_group_value(self) -> None:
        """Test SYMPTOM_GROUP value."""
        assert ClinicalCodeType.SYMPTOM_GROUP == "Symptom Group (SG)"

    def test_symptom_discriminator_value(self) -> None:
        """Test SYMPTOM_DISCRIMINATOR value."""
        assert ClinicalCodeType.SYMPTOM_DISCRIMINATOR == "Symptom Discriminator (SD)"

    def test_disposition_value(self) -> None:
        """Test DISPOSITION value."""
        assert ClinicalCodeType.DISPOSITION == "Disposition (Dx)"

    def test_sg_sd_pair_value(self) -> None:
        """Test SG_SD_PAIR value."""
        assert ClinicalCodeType.SG_SD_PAIR == "Symptom Group and Symptom Discriminator Pair (SG-SD)"

    def test_clinical_code_type_members(self) -> None:
        """Test that ClinicalCodeType has exactly 4 members."""
        members = list(ClinicalCodeType)
        assert len(members) == 4


class TestTimeUnit:
    """Tests for TimeUnit enum."""

    def test_days_value(self) -> None:
        """Test DAYS value."""
        assert TimeUnit.DAYS == "days"

    def test_months_value(self) -> None:
        """Test MONTHS value."""
        assert TimeUnit.MONTHS == "months"

    def test_years_value(self) -> None:
        """Test YEARS value."""
        assert TimeUnit.YEARS == "years"

    def test_time_unit_members(self) -> None:
        """Test that TimeUnit has exactly 3 members."""
        members = list(TimeUnit)
        assert len(members) == 3


class TestTelecomType:
    """Tests for TelecomType enum."""

    def test_phone_value(self) -> None:
        """Test PHONE value."""
        assert TelecomType.PHONE == "phone"

    def test_email_value(self) -> None:
        """Test EMAIL value."""
        assert TelecomType.EMAIL == "email"

    def test_web_value(self) -> None:
        """Test WEB value."""
        assert TelecomType.WEB == "web"

    def test_telecom_type_members(self) -> None:
        """Test that TelecomType has exactly 3 members."""
        members = list(TelecomType)
        assert len(members) == 3

    def test_telecom_type_is_string_enum(self) -> None:
        """Test that TelecomType values work as strings."""
        assert TelecomType.PHONE.value == "phone"
        assert TelecomType.EMAIL.value == "email"
