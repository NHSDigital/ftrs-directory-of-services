from pydantic_settings import BaseSettings
from pydantic import Field


class TestSettings(BaseSettings):
    environment: str = "local"
    workspace: str | None = None
    use_existing_crud_api: bool = False
    crud_api_endpoint: str | None = None
    existing_dynamodb_endpoint: str | None = None
