import re
from typing import Type

from fhir.resources import FHIRAbstractModel
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from ftrs_common.logbase import FhirLogBase
from ftrs_common.logger import Logger
from pydantic import ValidationError

fhir_logger = Logger.get(service="common_fhir_logger")


class FhirValidator:
    @staticmethod
    def _validate_resource_structure(
        resource: dict, fhir_model: Type[FHIRAbstractModel]
    ) -> dict:
        """
        Validates that the resource is a properly structured JSON object.
        Returns the resource if valid, raises OperationOutcomeException if not.
        """
        if not isinstance(resource, dict):
            msg = "Invalid request body: must be a JSON object"
            FhirValidator._log_and_raise(msg, "structure", fhir_model)

        if "resourceType" not in resource:
            msg = "Missing required field 'resourceType'"
            FhirValidator._log_and_raise(msg, "structure", fhir_model)

        expected_type = fhir_model.__name__
        if resource["resourceType"] != expected_type:
            msg = f"Invalid resourceType: must be '{expected_type}'"
            FhirValidator._log_and_raise(msg, "structure", fhir_model)

        return resource

    @staticmethod
    def _check_for_special_characters(
        resource: dict, fhir_model: Type[FHIRAbstractModel]
    ) -> dict:
        """
        Validates that the name, modifiedBy, telecom, and type fields do not contain special characters.
        Returns the resource if valid, raises OperationOutcomeException if not.
        """
        special_characters_pattern = r"[\'\";\\/\`=<>%|&#*@$]"

        for field in ["name", "modifiedBy", "telecom", "type"]:
            value = resource.get(field)
            if isinstance(value, str) and re.search(special_characters_pattern, value):
                msg = f"Field '{field}' contains invalid characters: {value}"
                FhirValidator._log_and_raise(msg, "invalid", fhir_model)

        return resource

    @staticmethod
    def _log_and_raise(
        msg: str, code: str, fhir_model: Type[FHIRAbstractModel]
    ) -> None:
        fhir_logger.log(
            FhirLogBase.FHIR_001,
            resource_type=fhir_model.__name__,
            error=msg,
        )
        raise OperationOutcomeException(
            OperationOutcomeHandler.build(
                diagnostics=msg,
                code=code,
                severity="error",
            )
        )

    @staticmethod
    def validate(
        resource: dict, fhir_model: Type[FHIRAbstractModel]
    ) -> FHIRAbstractModel:
        """
        Validates the given resource against the provided FHIR model.
        Returns an instance of the model if validation is successful.
        Raises OperationOutcomeException if validation fails.
        """
        resource = FhirValidator._validate_resource_structure(resource, fhir_model)
        resource = FhirValidator._check_for_special_characters(resource, fhir_model)
        try:
            return fhir_model.model_validate(resource)
        except ValidationError as e:
            fhir_logger.log(
                FhirLogBase.FHIR_001,
                status_code=422,
                resource_type=fhir_model.__name__,
                error=str(e),
            )
            outcome = OperationOutcomeHandler.from_validation_error(e)
            raise OperationOutcomeException(outcome)
