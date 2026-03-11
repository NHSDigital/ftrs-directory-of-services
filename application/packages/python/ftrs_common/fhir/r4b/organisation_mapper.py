from fhir.resources.R4B.bundle import Bundle, BundleEntry, BundleEntrySearch, BundleLink
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganisation
from ftrs_common.fhir.base_mapper import FhirMapper
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_common.utils.title_case_sanitization import sanitize_string_field
from ftrs_data_layer.domain import Organisation, Telecom
from ftrs_data_layer.domain.enums import OrganisationTypeCode, TelecomType
from ftrs_data_layer.domain.organisation import LegalDates

VALID_PRIMARY_TYPE_CODES = {
    OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
}


TYPED_PERIOD_URL = (
    "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
)
ORGANISATION_ROLE_URL = (
    "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
)
ROLE_CODE_URL = "roleCode"
ROLE_CODE_SYSTEM_URL = "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole"


class OrganizationMapper(FhirMapper):
    # --- FHIR Builders ---
    def _build_meta_profile(self) -> dict:
        return {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
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

    def _build_telecom(self, telecom: list[Telecom] | str | None) -> list[dict]:
        """Build FHIR telecom list from phone, email and web."""
        # Temporary handling for string and None telecom (old data format)
        if not telecom:
            return []
        if isinstance(telecom, str):
            return [
                ContactPoint.model_validate(
                    {"system": TelecomType.PHONE.to_fhir_value(), "value": telecom}
                )
            ]
        fhir_telecom = []
        for tel in telecom:
            fhir_telecom.append(
                ContactPoint.model_validate(
                    {"system": tel.type.to_fhir_value(), "value": tel.value}
                )
            )
        return fhir_telecom

    def _build_organisation_extensions(
        self, organisation: Organisation
    ) -> list[Extension]:
        extensions = []
        legal_start_str, legal_end_str = self._get_legal_dates(organisation)

        # Add primary role extension with legal dates
        if organisation.primary_role_code:
            primary_ext = self._build_organisation_role_extension(
                organisation.primary_role_code,
                legal_start_str,
                legal_end_str,
                active=organisation.active,
            )
            if primary_ext:
                extensions.append(primary_ext)

        # Add non-primary role extensions without legal dates
        if organisation.non_primary_role_codes:
            for role_code in organisation.non_primary_role_codes:
                non_primary_ext = self._build_organisation_role_extension(role_code)
                if non_primary_ext:
                    extensions.append(non_primary_ext)

        return extensions

    def _build_organisation_role_extension(
        self,
        role_code: str | None,
        legal_start_date: str | None = None,
        legal_end_date: str | None = None,
        active: bool | None = False,
    ) -> Extension | None:
        """
        Build FHIR OrganisationRole extension with role code and optional legal dates.

        Structure:
        - OrganisationRole (top level)
            - roleCode (nested)
            - TypedPeriod (nested, optional - only if legal dates provided)
        """
        extension_list = [
            {
                "url": ROLE_CODE_URL,
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": ROLE_CODE_SYSTEM_URL,
                            "code": role_code,
                            "display": role_code,
                        }
                    ]
                },
            }
        ]

        typed_period_ext = self._build_typed_period_extension(
            legal_start_date, legal_end_date
        )
        if typed_period_ext:
            extension_list.append(typed_period_ext.model_dump())

        if legal_start_date and legal_end_date:
            extension_list.append({"url": "active", "valueBoolean": active})

        return Extension.model_validate(
            {
                "url": ORGANISATION_ROLE_URL,
                "extension": extension_list,
            }
        )

    def _build_typed_period_extension(
        self, legal_start_date: str | None, legal_end_date: str | None
    ) -> Extension | None:
        """Build FHIR TypedPeriod extension for legal dates using Extension model."""
        if not legal_start_date and not legal_end_date:
            return None
        period_data = {}
        if legal_start_date:
            period_data["start"] = legal_start_date
        if legal_end_date:
            period_data["end"] = legal_end_date
        return Extension.model_validate(
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

    def _build_legal_dates_from_fhir(
        self, fhir_resource: FhirOrganisation
    ) -> LegalDates | None:
        """
        Extract and build LegalDates domain object from FHIR resource.
        Returns None if no legal dates are present.
        """
        legal_start_date, legal_end_date = self._extract_legal_dates(fhir_resource)

        if legal_start_date or legal_end_date:
            return LegalDates(start=legal_start_date, end=legal_end_date)

        return None

    # --- Domain <-> FHIR Conversion ---
    def to_fhir(self, organisation: Organisation) -> FhirOrganisation:
        org_dict = {
            "resourceType": "Organization",
            "id": str(organisation.id),
            "meta": self._build_meta_profile(),
            "active": organisation.active,
            "name": organisation.name,
            "identifier": self._build_identifier(organisation.identifier_ODS_ODSCode),
            "telecom": self._build_telecom(organisation.telecom),
        }
        extensions = self._build_organisation_extensions(organisation)
        if extensions:
            org_dict["extension"] = extensions
        return FhirOrganisation.model_validate(org_dict)

    def from_fhir(self, fhir_resource: FhirOrganisation) -> Organisation:
        """Convert FHIR Organization resource to Organisation domain object."""
        primary_code, non_primary_codes = self._extract_role_codes_from_fhir(
            fhir_resource
        )
        legal_dates = self._build_legal_dates_from_fhir(fhir_resource)
        return Organisation(
            identifier_ODS_ODSCode=fhir_resource.identifier[0].value,
            id=str(fhir_resource.id),
            name=sanitize_string_field(fhir_resource.name),
            active=fhir_resource.active,
            telecom=self._get_org_telecom(fhir_resource),
            legalDates=legal_dates,
            lastUpdatedBy={
                "type": "app",
                "value": "apim_product_id",
                "display": "API Management",
            },
            primary_role_code=primary_code,
            non_primary_role_codes=non_primary_codes,
        )

    def to_fhir_bundle(
        self,
        organisations: list[Organisation],
        request_url: str | None = None,
    ) -> Bundle:
        """Convert list of Organisation objects to FHIR Bundle (searchset).

        Returns a FHIR-compliant Bundle containing minimal Organization resources with only id and meta.
        Each entry has search.mode set to "match" indicating the resource matched the search criteria.

        Args:
            organisations: List of Organisation domain objects
            request_url: The request URL for the Bundle self link

        Returns:
            FHIR Bundle with Organization resources
        """
        entries = [self._create_bundle_entry(org, request_url) for org in organisations]

        bundle_dict = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(entries),
            "entry": entries,
        }

        if request_url:
            bundle_dict["link"] = [
                BundleLink.model_validate({"relation": "self", "url": request_url})
            ]

        return Bundle.model_construct(**bundle_dict)

    def _create_bundle_entry(
        self, org: Organisation, request_url: str | None = None
    ) -> BundleEntry:
        """Create a FHIR Bundle entry with Organization resource."""
        full_org = self.to_fhir(org)

        # Remove extensions
        full_org.extension = None

        entry_dict = {
            "resource": full_org,
            "search": BundleEntrySearch.model_validate({"mode": "match"}),
        }

        if request_url:
            base_url = self._extract_base_url(request_url)
            entry_dict["fullUrl"] = f"{base_url}/Organization/{org.id}"

        return BundleEntry.model_construct(**entry_dict)

    def _extract_base_url(self, request_url: str) -> str:
        if "?" in request_url:
            return request_url.split("?")[0].rsplit("/", 1)[0]
        return request_url.rsplit("/", 1)[0]

    def from_ods_fhir_to_fhir(
        self, ods_fhir_organization: dict
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
            "identifier": self._build_identifier(ods_code),
            "telecom": ods_fhir_organization.get("telecom", []),
        }
        extensions_dict = ods_fhir_organization.get("extension", [])
        extensions = [
            Extension.model_validate(ext_dict) for ext_dict in extensions_dict
        ]

        role_extensions = [e for e in extensions if e.url == ORGANISATION_ROLE_URL]

        if role_extensions:
            required_fields["extension"] = role_extensions

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

    def _get_org_telecom(self, fhir_org: FhirOrganisation) -> list[Telecom]:
        """Extract telecom (phone, email, web) from FHIR Organization telecom."""
        if not (hasattr(fhir_org, "telecom") and fhir_org.telecom):
            return []

        telecoms = []
        for telecom in fhir_org.telecom:
            telecoms.append(
                Telecom(
                    type=TelecomType.from_fhir_value(telecom.system),
                    value=telecom.value,
                    isPublic=True,
                )
            )
        return telecoms

    def _extract_all_role_codes(self, extensions: list[Extension]) -> list[str]:
        """Extract all role codes from organization extensions."""
        role_codes = []
        for ext in extensions:
            if getattr(ext, "url", None) == ORGANISATION_ROLE_URL:
                role_code = self._get_role_code(ext)
                if role_code:
                    role_codes.append(role_code)
        return role_codes

    def _is_legal_typed_period(self, ext: Extension) -> bool:
        """
        Check if a TypedPeriod Extension has dateType 'Legal'.
        """
        for sub_ext in ext.extension:
            if (
                getattr(sub_ext, "url", None) == "dateType"
                and getattr(sub_ext, "valueCoding", None)
                and getattr(sub_ext.valueCoding, "code", None) == "Legal"
            ):
                return True
        return False

    def get_primary_and_non_primary_role_codes(
        self, role_codes: list[str]
    ) -> tuple[str | None, list[str]]:
        """
        Extract primary and non-primary organization role codes from role codes.

        Primary roles are:
        - RO182 (Pharmacy)
        - RO177 (Prescribing Cost Centre)

        Args:
            role_codes: List of ODS role codes

        Returns:
            Tuple of (primary_role_code, non_primary_role_codes)
        """

        if len(role_codes) == 0:
            return None, []

        primary_code = None
        non_primary_codes = []

        for role_code in role_codes:
            if role_code in [code.value for code in VALID_PRIMARY_TYPE_CODES]:
                primary_code = role_code
            else:
                non_primary_codes.append(role_code)

        return primary_code, non_primary_codes

    def _get_role_code(self, ext: Extension) -> str | None:
        """Extract role code from OrganisationRole Extension object."""
        for sub_ext in getattr(ext, "extension", []):
            if getattr(sub_ext, "url", None) == ROLE_CODE_URL:
                value_codeable_concept = getattr(sub_ext, "valueCodeableConcept", None)
                if value_codeable_concept:
                    coding = getattr(value_codeable_concept, "coding", None)
                    if coding:
                        return getattr(coding[0], "code", None)
        return None

    def _extract_role_codes_from_fhir(
        self, fhir_resource: FhirOrganisation
    ) -> tuple[str | None, list[str]]:
        """
        Extract primary and non-primary role codes from FHIR resource.

        Returns:
            Tuple of (primary_role_code, non_primary_role_codes)
        """
        extensions = getattr(fhir_resource, "extension", None)
        if not extensions:
            return None, []

        role_codes = self._extract_all_role_codes(extensions)
        return self.get_primary_and_non_primary_role_codes(role_codes)

    def _find_legal_typed_period_in_role(self, ext: Extension) -> Extension | None:
        """Find Legal TypedPeriod within an OrganisationRole extension."""
        for sub_ext in ext.extension:
            if getattr(
                sub_ext, "url", None
            ) == TYPED_PERIOD_URL and self._is_legal_typed_period(sub_ext):
                return sub_ext
        return None

    def _get_typed_period_extension(
        self, extensions: list[Extension] | None
    ) -> Extension | None:
        """
        Return the Legal TypedPeriod Extension object from extensions (list of Extension).
        Searches within OrganisationRole extensions for TypedPeriod with dateType 'Legal'.
        """
        if not extensions:
            return None
        for ext in extensions:
            if getattr(ext, "url", None) != ORGANISATION_ROLE_URL:
                continue
            if not getattr(ext, "extension", None):
                continue

            legal_period = self._find_legal_typed_period_in_role(ext)
            if legal_period:
                return legal_period

        return None

    def _parse_legal_period(
        self, typed_period_ext: Extension | None
    ) -> tuple[str | None, str | None]:
        """Extract start and end dates from validated TypedPeriod Extension."""
        if not typed_period_ext or not typed_period_ext.extension:
            return None, None

        period_ext = next(
            (e for e in typed_period_ext.extension if e.url == "period"), None
        )

        if not period_ext or not period_ext.valuePeriod:
            return None, None

        start = getattr(period_ext.valuePeriod, "start", None)
        end = getattr(period_ext.valuePeriod, "end", None)

        return start, end

    def _extract_legal_dates(
        self, resource: FhirOrganisation
    ) -> tuple[str | None, str | None]:
        """Extract legal dates from TypedPeriod extension in FHIR resource."""
        extensions = getattr(resource, "extension", None)
        typed_period_ext = self._get_typed_period_extension(extensions)
        return self._parse_legal_period(typed_period_ext)
