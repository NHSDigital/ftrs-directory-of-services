from boto3.dynamodb.types import TypeDeserializer
from ftrs_common.feature_flags import FeatureFlag, is_enabled
from ftrs_common.utils.db_service import get_table_name
from ftrs_data_layer.client import get_dynamodb_client
from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.logbase import DataMigrationLogBase
from sqlalchemy import and_
from sqlmodel import Session, select

from service_migration.exceptions import ServiceMigrationException
from service_migration.models import ServiceMigrationState
from service_migration.transformer.base import (
    ServiceTransformer,
    ServiceTransformOutput,
)
from service_migration.transformer.base_pharmacy import BasePharmacyTransformer


class BasePharmacyBPCheckTransformer(ServiceTransformer):
    STATUS_ACTIVE = 1
    ODS_BASE_LENGTH = 5
    NAME_PREFIXES = ("BP Check:", "BP:")
    SERVICE_TYPE_ID: int
    ODS_SUFFIX: str

    def __init__(
        self,
        logger,
        metadata,
        dynamodb_endpoint: str | None = None,
    ) -> None:
        super().__init__(
            logger=logger,
            metadata=metadata,
            dynamodb_endpoint=dynamodb_endpoint,
        )
        self._deserializer = TypeDeserializer()

    def transform(self, service: legacy_model.Service) -> ServiceTransformOutput:
        base_ods_code = service.odscode[: self.ODS_BASE_LENGTH]
        parent_service = self._get_parent_service(base_ods_code)
        if parent_service is None:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_038,
                service_id=service.id,
                base_ods_code=base_ods_code,
            )
            raise ServiceMigrationException(
                f"Parent pharmacy record not found for base ODS code {base_ods_code}",
                requeue=False,
            )

        parent_state = self._get_state_record(parent_service.id)
        if not parent_state:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_038,
                service_id=service.id,
                base_ods_code=base_ods_code,
            )
            raise ServiceMigrationException(
                f"Parent pharmacy record not found in state for base ODS code {base_ods_code}",
                requeue=False,
            )

        if not parent_state.organisation_id or not parent_state.location_id:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_038,
                service_id=service.id,
                base_ods_code=base_ods_code,
            )
            raise ServiceMigrationException(
                "Parent pharmacy state record is missing organisation or location",
                requeue=False,
            )

        healthcare_service = self.build_healthcare_service(
            service,
            parent_state.organisation_id,
            parent_state.location_id,
            category=HealthcareServiceCategory.PHARMACY_SERVICES,
            type=HealthcareServiceType.ESSENTIAL_SERVICES,
        )

        return ServiceTransformOutput(
            organisation=[],
            healthcare_service=[healthcare_service],
            location=[],
        )

    @classmethod
    def is_service_supported(  # noqa: PLR0911
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        if not is_enabled(FeatureFlag.DATA_MIGRATION_PHARMACY_ENABLED):
            return (
                False,
                "Pharmacy service selection is disabled by feature flag",
            )

        if service.typeid != cls.SERVICE_TYPE_ID:
            return (
                False,
                f"Service type is not a Pharmacy type ({cls.SERVICE_TYPE_ID})",
            )

        if not service.odscode:
            return False, "Service does not have an ODS code"

        expected_length = cls.ODS_BASE_LENGTH + len(cls.ODS_SUFFIX)
        if len(service.odscode) != expected_length:
            return False, f"ODS code is not {expected_length} characters"

        if not service.odscode.endswith(cls.ODS_SUFFIX):
            return False, f"ODS code does not end with {cls.ODS_SUFFIX}"

        base_ods_code = service.odscode[: cls.ODS_BASE_LENGTH]
        matches_f_prefix = (
            BasePharmacyTransformer.PHARMACY_ODS_CODE_REGEX_F_PREFIX.match(
                base_ods_code
            )
        )
        matches_alternating = (
            BasePharmacyTransformer.PHARMACY_ODS_CODE_REGEX_ALTERNATING.match(
                base_ods_code
            )
        )

        if not (matches_f_prefix or matches_alternating):
            return (
                False,
                "ODS code does not match required format (F + 4 alphanumeric OR alternating letter-number)",
            )

        return True, None

    @classmethod
    def should_include_service(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        if service.statusid != cls.STATUS_ACTIVE:
            return False, "Service is not active"

        if not service.name:
            return False, "Service name is missing"

        if not any(service.name.startswith(prefix) for prefix in cls.NAME_PREFIXES):
            return (
                False,
                "Service name does not start with required prefix (BP Check: or BP:)",
            )

        return True, None

    def _get_parent_service(self, base_ods_code: str) -> legacy_model.Service | None:
        with Session(self.metadata.engine) as session:
            stmt = select(legacy_model.Service).where(
                and_(
                    legacy_model.Service.odscode == base_ods_code,
                    legacy_model.Service.typeid == self.SERVICE_TYPE_ID,
                )
            )
            record = session.exec(stmt).first()
            if not record:
                return None

            return legacy_model.Service(
                **record.model_dump(mode="python", warnings=False),
                endpoints=list(record.endpoints),
                scheduled_opening_times=list(record.scheduled_opening_times),
                specified_opening_times=list(record.specified_opening_times),
                sgsds=list(record.sgsds),
                dispositions=list(record.dispositions),
                age_range=list(record.age_range),
            )

    def _get_state_record(self, service_id: int) -> ServiceMigrationState | None:
        dynamodb_client = get_dynamodb_client(self.dynamodb_endpoint)
        state_table = get_table_name("data-migration-state")
        source_record_id = ServiceMigrationState.format_source_record_id(service_id)

        response = dynamodb_client.get_item(
            TableName=state_table,
            Key={"source_record_id": {"S": source_record_id}},
            ConsistentRead=True,
        )

        item = response.get("Item")
        if not item:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_020,
                record_id=service_id,
            )
            return None

        deserialized_data = {
            k: self._deserializer.deserialize(v) for k, v in item.items()
        }
        self.logger.log(
            DataMigrationLogBase.DM_ETL_019,
            record_id=service_id,
        )
        return ServiceMigrationState.model_validate(deserialized_data)


class PharmacyBPCheckTransformer(BasePharmacyBPCheckTransformer):
    SERVICE_TYPE_ID = 13
    ODS_SUFFIX = "BPS"


class PharmacyDSPBPCheckTransformer(BasePharmacyBPCheckTransformer):
    SERVICE_TYPE_ID = 134
    ODS_SUFFIX = "DSPBPS"
