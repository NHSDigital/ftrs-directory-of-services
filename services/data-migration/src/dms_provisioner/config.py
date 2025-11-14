from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

from common.config import DatabaseConfig
from common.secret_utils import get_secret


class DmsDatabaseConfig(BaseSettings):
    """Handles configuration and environment variables for the DMS pipeline."""

    target_rds_details: str = Field(..., alias="TARGET_RDS_DETAILS")
    dms_user_details: str = Field(..., alias="DMS_USER_DETAILS")
    trigger_lambda_arn: str = Field(..., alias="TRIGGER_LAMBDA_ARN")

    def get_target_rds_config(self) -> DatabaseConfig:
        """Get target RDS details using the existing DatabaseConfig infrastructure."""
        target_rds_details_secret = get_secret(
            self.target_rds_details, transform="json"
        )
        return DatabaseConfig(**target_rds_details_secret)

    def get_dms_user_details(self) -> tuple[str, SecretStr]:
        """Get DMS user details using existing secret retrieval methods."""
        rds_password = get_secret(self.dms_user_details)
        rds_username = "dms_user"
        return rds_username, rds_password
