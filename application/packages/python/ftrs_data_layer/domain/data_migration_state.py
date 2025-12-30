from uuid import UUID

from boto3.dynamodb.types import TypeDeserializer
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.domain.base import DBModel


class DataMigrationState(DBModel):
    source_record_id: str
    version: int
    organisation_id: UUID
    organisation: Organisation
    location_id: UUID
    location: Location
    healthcare_service_id: UUID
    healthcare_service: HealthcareService

    @classmethod
    def from_dynamodb_item(cls, item: dict) -> "DataMigrationState":
        """
        Deserialize a DynamoDB item into a DataMigrationState object.

        Args:
            item: DynamoDB item in type-annotated format (e.g., {"S": "value", "N": "123"})

        Returns:
            DataMigrationState object with properly typed fields
        """
        deserializer = TypeDeserializer()

        # Deserialize all fields from DynamoDB format to Python types
        python_data = {k: deserializer.deserialize(v) for k, v in item.items()}

        # Parse nested model objects
        return cls(
            id=UUID(python_data["id"]),
            source_record_id=python_data["source_record_id"],
            version=python_data["version"],
            organisation_id=UUID(python_data["organisation_id"]),
            organisation=Organisation(**python_data["organisation"]),
            location_id=UUID(python_data["location_id"]),
            location=Location(**python_data["location"]),
            healthcare_service_id=UUID(python_data["healthcare_service_id"]),
            healthcare_service=HealthcareService(**python_data["healthcare_service"]),
        )
