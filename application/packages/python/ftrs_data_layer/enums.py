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


class HealthcareServiceCategory(str, Enum):
    GP_SERVICES = "GP Services"


class HealthcareServiceType(str, Enum):
    GP_CONSULTATION_SERVICE = "GP Consultation Service"
    PCN_SERVICE = "Primary Care Network Enhanced Access Service"


class EndpointStatus(str, Enum):
    ACTIVE = "active"
    OFF = "off"


class EndpointConnectType(str, Enum):
    ITK = "itk"
    EMAIL = "email"
    TELNO = "telno"
    HTTP = "http"


class EndpointDescription(str, Enum):
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
