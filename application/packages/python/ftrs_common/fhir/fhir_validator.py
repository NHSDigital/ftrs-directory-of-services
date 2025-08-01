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
    def validate(
        resource: dict, fhir_model: Type[FHIRAbstractModel]
    ) -> FHIRAbstractModel:
        """
        Validates the given resource against the provided FHIR model.
        Returns an instance of the model if validation is successful.
        Raises OperationOutcomeException if validation fails.
        """
        try:
            return fhir_model.model_validate(resource)
        except (ValidationError, TypeError, KeyError) as e:
            fhir_logger.log(
                FhirLogBase.FHIR_001,
                status_code=422,
                resource_type=fhir_model.__name__,
                error=str(e),
            )
            outcome = OperationOutcomeHandler.from_validation_error(e)
            raise OperationOutcomeException(outcome)
