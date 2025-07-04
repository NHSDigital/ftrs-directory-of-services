from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError

from functions.error_util import (
    create_resource_internal_server_error,
    create_resource_validation_error,
)


def create_validation_error():
    try:
        from pydantic import BaseModel, Field

        class TestModel(BaseModel):
            test_field: str = Field(min_length=5)

        TestModel(test_field="abc")
    except ValidationError as e:
        return e
    else:
        return None


class TestErrorUtil:
    def test_create_resource_internal_server_error(self):
        # Act
        result = create_resource_internal_server_error()

        # Assert
        assert isinstance(result, OperationOutcome)
        assert result.id == "internal-server-error"
        assert len(result.issue) == 1
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "internal"
        assert result.issue[0].details.coding[0].code == "INTERNAL_SERVER_ERROR"

    def test_create_resource_validation_error(self):
        # Arrange
        validation_error = create_validation_error()

        # Act
        result = create_resource_validation_error(validation_error)

        # Assert
        assert isinstance(result, OperationOutcome)
        assert result.id == "ods-code-validation-error"
        assert len(result.issue) == 1
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "invalid"
        assert result.issue[0].details.coding[0].code == "INVALID_ODS_CODE_FORMAT"
        assert result.issue[0].diagnostics == validation_error.errors()[0]["msg"]
        assert result.issue[0].expression == [validation_error.errors()[0]["input"]]
