from enum import Enum


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


class OrganisationType(str, Enum):
    GP_PRACTICE = "GP Practice"

class OrganisationTypeCode(str, Enum):
    PRESCRIBING_COST_CENTRE_CODE = "RO177"
    GP_PRACTICE_ROLE_CODE = "RO76"
    OUT_OF_HOURS_ROLE_CODE = "RO80"
    WALK_IN_CENTRE_ROLE_CODE = "RO87"
    PHARMACY_ROLE_CODE = "RO182"


class HealthcareServiceCategory(str, Enum):
    GP_SERVICES = "GP Services"


class HealthcareServiceType(str, Enum):
    GP_CONSULTATION_SERVICE = "GP Consultation Service"
    PCN_SERVICE = "Primary Care Network Enhanced Access Service"


class EndpointStatus(str, Enum):
    ACTIVE = "active"
    OFF = "off"


class EndpointConnectionType(str, Enum):
    ITK = "itk"
    EMAIL = "email"
    TELNO = "telno"
    HTTP = "http"


class EndpointBusinessScenario(str, Enum):
    PRIMARY = "Primary"
    COPY = "Copy"


class EndpointPayloadType(str, Enum):
    ED = "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0"
    GP_PRIMARY = "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0"
    GP_COPY = "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0"
    OTHER = "urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0"
    AMBULANCE = "urn:nhs-itk:interaction:primaryNHS111RequestforAmbulance-v2-0"  # TODO: review if this is real value
    SCHEDULING = "scheduling"  # TODO: review how to handle this


class EndpointPayloadMimeType(str, Enum):
    PDF = "application/pdf"
    HTML = "text/html"
    FHIR = "application/fhir"
    XML = "xml"
    EMAIL = "message/rfc822"
    TELNO = "text/vcard"
    CDA = "application/hl7-cda+xml"


class ClinicalCodeSource(str, Enum):
    PATHWAYS = "pathways"
    SERVICE_FINDER = "servicefinder"


class ClinicalCodeType(str, Enum):
    SYMPTOM_GROUP = "Symptom Group (SG)"
    SYMPTOM_DISCRIMINATOR = "Symptom Discriminator (SD)"
    DISPOSITION = "Disposition (Dx)"
    SG_SD_PAIR = "Symptom Group and Symptom Discriminator Pair (SG-SD)"


class TimeUnit(str, Enum):
    DAYS = "days"
    MONTHS = "months"
    YEARS = "years"


class TelecomType(str, Enum):
    PHONE = "phone"
    EMAIL = "email"
    WEB = "web"

    def to_fhir_value(self) -> str:
        if self == TelecomType.WEB:
            return "url"
        return self.value

    @staticmethod
    def from_fhir_value(value: str) -> "TelecomType":
        if value is None:
            msg = "Telecom type (system) cannot be None or empty"
            raise ValueError(msg)
        if value == "url":
            return TelecomType.WEB
        for telecom_type in TelecomType:
            if telecom_type.value == value:
                return telecom_type
        raise ValueError("invalid telecom type (system): " + value)
