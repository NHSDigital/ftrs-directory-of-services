from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganisation
from ftrs_common.fhir.base_mapper import FhirMapper
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_data_layer.domain import Organisation


class OrganizationMapper(FhirMapper):
    # --- FHIR Builders ---
    def _build_meta_profile(self) -> dict:
        return {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        }

    def _build_identifier(self, ods_code: str) -> list[Identifier]:
        """Build FHIR identifier list with ODS organization code."""
        return [
            Identifier.model_validate(
                {
                    "use": "official",
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": ods_code,
                }
            )
        ]

    def _build_telecom(self, telecom: str | None) -> list[dict]:
        """Build FHIR telecom list from phone number."""
        return [{"system": "phone", "value": telecom, "use": "work"}] if telecom else []

    def _build_type(self, org_type_value: str) -> list[CodeableConcept]:
        """Build FHIR organization type CodeableConcept."""
        return [
            CodeableConcept.model_validate(
                {
                    "coding": [
                        {
                            "system": "TO-DO",  # Use correct FHIR when defined
                            "code": org_type_value,
                            "display": org_type_value,
                        }
                    ],
                    "text": org_type_value,
                }
            )
        ]

    # --- Domain <-> FHIR Conversion ---
    def to_fhir(self, organisation: Organisation) -> FhirOrganisation:
        """Convert Organisation domain object to FHIR Organization resource."""
        org_dict = {
            "resourceType": "Organization",
            "id": str(organisation.id),
            "meta": self._build_meta_profile(),
            "active": organisation.active,
            "name": organisation.name,
            "type": self._build_type(getattr(organisation, "type", None)),
            "identifier": self._build_identifier(organisation.identifier_ODS_ODSCode),
            "telecom": self._build_telecom(organisation.telecom),
        }
        return FhirOrganisation.model_validate(org_dict)

    def from_fhir(self, fhir_resource: FhirOrganisation) -> Organisation:
        """Convert FHIR Organization resource to Organisation domain object."""
        return Organisation(
            identifier_ODS_ODSCode=fhir_resource.identifier[0].value,
            id=str(fhir_resource.id),
            name=fhir_resource.name,
            active=fhir_resource.active,
            telecom=self._get_org_telecom(fhir_resource),
            type=self._get_org_type(fhir_resource),
            modifiedBy="ODS_ETL_PIPELINE",
        )

    def to_fhir_bundle(self, organisations: list[Organisation]) -> Bundle:
        """Convert list of Organisation objects to FHIR Bundle (searchset)."""
        entries = [
            BundleEntry.model_construct(resource=self.to_fhir(org))
            for org in organisations
        ]

        bundle = Bundle.model_construct()
        bundle.type = "searchset"
        bundle.total = len(entries)
        bundle.entry = entries
        return bundle

    def from_ods_fhir_to_fhir(
        self, ods_fhir_organization: dict, dos_org_type: str
    ) -> FhirOrganisation | None:
        ods_code = self._extract_ods_code_from_identifiers(
            ods_fhir_organization.get("identifier", [])
        )

        required_fields = {
            "resourceType": "Organization",
            "id": ods_fhir_organization.get("id"),
            "meta": self._build_meta_profile(),
            "active": ods_fhir_organization.get("active"),
            "name": ods_fhir_organization.get("name"),
            "type": self._build_type(dos_org_type),
            "identifier": self._build_identifier(ods_code),
            "telecom": ods_fhir_organization.get("telecom", []),
        }
        return FhirValidator.validate(required_fields, FhirOrganisation)

    # --- FHIR Extraction Helpers ---
    def _extract_ods_code_from_identifiers(self, identifiers: list[dict]) -> str:
        """Extract ODS code from identifier list."""
        for identifier in identifiers:
            if not isinstance(identifier, dict):
                continue
            ods_org_code_system = "https://fhir.nhs.uk/Id/ods-organization-code"
            if identifier.get("system") == ods_org_code_system and identifier.get(
                "value"
            ):
                return identifier["value"]
        err_msg = "No ODS code identifier found in organization resource"
        raise ValueError(err_msg)

    def _get_org_type(self, fhir_org: FhirOrganisation) -> str | None:
        """Extract organization type from FHIR Organization resource
        If human readable text present use it, else use text in coding."""
        if not (hasattr(fhir_org, "type") and fhir_org.type):
            return None

        type_obj = fhir_org.type[0]
        if text := getattr(type_obj, "text", None):
            return text
        if coding := getattr(type_obj, "coding", None):
            return coding[0].display
        return None

    def _get_org_telecom(self, fhir_org: FhirOrganisation) -> str | None:
        """Extract phone number from FHIR Organization telecom."""
        if not (hasattr(fhir_org, "telecom") and fhir_org.telecom):
            return None

        for telecom in fhir_org.telecom:
            if getattr(telecom, "system", None) == "phone":
                return telecom.value
        return None

    def _get_role_code_from_extension(self, ext: dict) -> str | None:
        """Extract role code from organization role extension."""
        for sub_ext in ext.get("extension", []):
            if sub_ext.get("url") == "roleCode":
                if value_codeable_concept := sub_ext.get("valueCodeableConcept"):
                    coding = value_codeable_concept.get("coding", [])
                    if coding:
                        return coding[0].get("code")
        return None

    def get_all_role_codes(self, ods_org: dict) -> list[str]:
        """
        Extract all role codes from ODS organization.

        Public method for use by ETL processes.

        Args:
            ods_org: ODS FHIR organization dictionary

        Returns:
            List of all role codes found in the organization extensions
        """
        role_codes = []
        role_url = "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"

        for ext in ods_org.get("extension", []):
            if ext.get("url") != role_url:
                continue

            role_code = self._get_role_code_from_extension(ext)
            if role_code is not None:
                role_codes.append(role_code)

        return role_codes
