from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganisation
from ftrs_common.fhir.base_mapper import FhirMapper
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_common.utils.title_case_sanitization import sanitize_string_field
from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.domain.organisation import LegalDates

TYPED_PERIOD_URL = (
    "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
)


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

    def _build_legal_date_extension(
        self, legal_start_date: str | None, legal_end_date: str | None
    ) -> Extension | None:
        """
        Build FHIR TypedPeriod extension for legal dates using Extension model.
        Args:
            legal_start_date: Legal start date in ISO 8601 format (YYYY-MM-DD)
            legal_end_date: Legal end date in ISO 8601 format (YYYY-MM-DD)
        Returns:
            Extension object if at least one date present, else None
        """
        if not legal_start_date and not legal_end_date:
            return None
        period_data = {}
        if legal_start_date:
            period_data["start"] = legal_start_date
        if legal_end_date:
            period_data["end"] = legal_end_date
        ext = Extension.model_validate(
            {
                "url": TYPED_PERIOD_URL,
                "extension": [
                    {
                        "url": "dateType",
                        "valueCoding": {
                            "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                            "code": "Legal",
                            "display": "Legal",
                        },
                    },
                    {
                        "url": "period",
                        "valuePeriod": period_data,
                    },
                ],
            }
        )
        return ext

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
        legal_start_str, legal_end_str = self._get_legal_dates(organisation)
        legal_date_ext = self._build_legal_date_extension(
            legal_start_str, legal_end_str
        )
        if legal_date_ext:
            org_dict["extension"] = [legal_date_ext]
        return FhirOrganisation.model_validate(org_dict)

    def from_fhir(self, fhir_resource: FhirOrganisation) -> Organisation:
        """Convert FHIR Organization resource to Organisation domain object."""
        legal_start_date, legal_end_date = self._extract_legal_dates(fhir_resource)

        legal_dates = None
        if legal_start_date or legal_end_date:
            legal_dates = LegalDates(start=legal_start_date, end=legal_end_date)

        return Organisation(
            identifier_ODS_ODSCode=fhir_resource.identifier[0].value,
            id=str(fhir_resource.id),
            name=sanitize_string_field(fhir_resource.name),
            active=fhir_resource.active,
            telecom=self._get_org_telecom(fhir_resource),
            type=sanitize_string_field(self._get_org_type(fhir_resource)),
            legalDates=legal_dates,
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
        # Only include TypedPeriod extension if present
        extensions = ods_fhir_organization.get("extension", [])
        typed_period_ext = next(
            (e for e in extensions if e.get("url") == TYPED_PERIOD_URL), None
        )
        if typed_period_ext:
            required_fields["extension"] = [typed_period_ext]
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

    def _get_legal_dates(
        self, organisation: Organisation
    ) -> tuple[str | None, str | None]:
        """Return legal start and end dates as ISO 8601 strings."""
        legal_dates = getattr(organisation, "legalDates", None)

        if not legal_dates:
            return None, None

        legal_start = getattr(legal_dates, "start", None)
        legal_end = getattr(legal_dates, "end", None)
        legal_start_str = legal_start.isoformat() if legal_start else None
        legal_end_str = legal_end.isoformat() if legal_end else None
        return legal_start_str, legal_end_str

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

    def _get_typed_period_extension(self, extensions: list | None) -> Extension | None:
        """Return the TypedPeriod Extension object from a list, or None."""
        if not extensions:
            return None
        for ext in extensions:
            ext_obj = (
                ext if isinstance(ext, Extension) else Extension.model_validate(ext)
            )
            if ext_obj.url == TYPED_PERIOD_URL and getattr(ext_obj, "extension", None):
                return ext_obj
        return None

    def _parse_legal_period(
        self, typed_period_ext: Extension | None
    ) -> tuple[str | None, str | None]:
        """Parse Legal period from TypedPeriod Extension object."""
        if not typed_period_ext or not getattr(typed_period_ext, "extension", None):
            return None, None
        ext_objs = [
            e if isinstance(e, Extension) else Extension.model_validate(e)
            for e in typed_period_ext.extension
        ]
        date_type = next((e for e in ext_objs if e.url == "dateType"), None)
        period = next((e for e in ext_objs if e.url == "period"), None)
        if (
            date_type
            and getattr(date_type, "valueCoding", None)
            and date_type.valueCoding.code == "Legal"
            and period
            and getattr(period, "valuePeriod", None)
        ):
            value_period = period.valuePeriod
            start = getattr(value_period, "start", None)
            end = getattr(value_period, "end", None)
            return start, end
        return None, None

    def _extract_legal_dates(
        self, resource: FhirOrganisation
    ) -> tuple[str | None, str | None]:
        """Extract legal dates from TypedPeriod extension in FHIR resource."""
        extensions = getattr(resource, "extension", None)
        typed_period_ext = self._get_typed_period_extension(extensions)
        return self._parse_legal_period(typed_period_ext)
