from ftrs_common.utils.config import Settings
from pydantic import Field


class GpSettings(Settings):
    fhir_base_url: str = Field(alias="FHIR_BASE_URL")
