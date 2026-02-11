from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.healthcareservice import (
    HealthcareService as FhirHealthcareService,
)
from fhir.resources.R4B.identifier import Identifier
from ftrs_data_layer.domain import HealthcareService


class HealthcareServiceMapper:
    def map_to_fhir_healthcare_service(
        self, healthcare_service: HealthcareService
    ) -> FhirHealthcareService:
        """Map a domain HealthcareService to a FHIR HealthcareService resource."""
        service_id = str(healthcare_service.id)
        name = healthcare_service.name

        fhir_healthcare_service = FhirHealthcareService.model_validate(
            {
                "id": service_id,
                "identifier": self._create_identifiers(healthcare_service),
                "name": name,
                "providedBy": self._create_provided_by_reference(healthcare_service),
                "location": self._create_location_references(healthcare_service),
                "type": self._create_type(healthcare_service),
                "telecom": self._create_telecom(healthcare_service),
                "endpoint": self._create_endpoint_references(healthcare_service),
            }
        )
        return fhir_healthcare_service

    def _create_identifiers(
        self, healthcare_service: HealthcareService
    ) -> list[Identifier]:
        identifiers = []

        if healthcare_service.identifier_oldDoS_uid:
            identifiers.append(
                Identifier.model_validate(
                    {
                        "use": "official",
                        "system": "https://fhir.nhs.uk/Id/dos-service-id",
                        "value": healthcare_service.identifier_oldDoS_uid,
                    }
                )
            )

        return identifiers

    def _create_provided_by_reference(
        self, healthcare_service: HealthcareService
    ) -> dict[str, str] | None:
        if healthcare_service.providedBy:
            return {"reference": f"Organization/{healthcare_service.providedBy}"}
        return None

    def _create_location_references(
        self, healthcare_service: HealthcareService
    ) -> list[dict[str, str]]:
        if healthcare_service.location:
            return [{"reference": f"Location/{healthcare_service.location}"}]
        return []

    def _create_endpoint_references(
        self, healthcare_service: HealthcareService
    ) -> list[dict[str, str]]:
        if healthcare_service.endpoint:
            references = []
            for endpoint_id in healthcare_service.endpoint:
                references.append({"reference": f"Endpoint/{endpoint_id}"})
            return references
        return []

    def _create_type(
        self, healthcare_service: HealthcareService
    ) -> list[CodeableConcept]:
        if not healthcare_service.type:
            return []

        type_value = (
            healthcare_service.type.value
            if hasattr(healthcare_service.type, "value")
            else str(healthcare_service.type)
        )

        return [
            CodeableConcept.model_validate(
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/ValueSet/service-type",
                            "code": type_value,
                            "display": type_value,
                        }
                    ],
                }
            )
        ]

    def _create_telecom(self, healthcare_service: HealthcareService) -> list[dict]:
        telecom_list = []

        if not healthcare_service.telecom:
            return telecom_list

        telecom = healthcare_service.telecom

        if telecom.phone_public:
            telecom_list.append(
                {
                    "system": "phone",
                    "value": telecom.phone_public,
                    "use": "work",
                    "extension": [
                        {
                            "url": "http://hl7.org/fhir/StructureDefinition/contactpoint-comment",
                            "valueString": "Public",
                        }
                    ],
                }
            )
        if telecom.phone_private:
            telecom_list.append(
                {
                    "system": "phone",
                    "value": telecom.phone_private,
                    "use": "work",
                    "extension": [
                        {
                            "url": "http://hl7.org/fhir/StructureDefinition/contactpoint-comment",
                            "valueString": "Clinician Access Only",
                        }
                    ],
                }
            )

        if telecom.email:
            telecom_list.append(
                {
                    "system": "email",
                    "value": telecom.email,
                }
            )

        if telecom.web:
            telecom_list.append(
                {
                    "system": "url",
                    "value": telecom.web,
                }
            )

        return telecom_list
