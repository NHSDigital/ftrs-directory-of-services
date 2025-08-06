from ftrs_common.utils.config import Settings

_settings = Settings()


def get_api_url(api_name: str) -> str:
    """Generate base URL for API based on API name, environment and workspace."""
    workspace_suffix = (
        f"-{_settings.workspace}"
        if _settings.workspace and _settings.workspace != "default"
        else ""
    )
    return f"https://{api_name}{workspace_suffix}.{_settings.env}.ftrs.cloud.nhs.uk"


def get_fhir_url(api_name: str, resource_type: str, resource_id: str = None) -> str:
    """Build FHIR URL from domain and resource details."""
    api_url = get_api_url(api_name)
    url = f"{api_url}/FHIR/R4/{resource_type}"
    return f"{url}/{resource_id}" if resource_id else url
