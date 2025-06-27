from typing import Type
from fhir.resources import FHIRAbstractModel
from ftrs_common.fhir.operation_outcome import OperationOutcomeException, OperationOutcomeHandler
from pydantic import ValidationError

class FhirValidator:

    @staticmethod
    def validate(
        resource: dict, fhir_model: Type[FHIRAbstractModel]
    ) -> FHIRAbstractModel:
        try:
            return fhir_model.model_validate(resource)
        except ValidationError as e:
            outcome = OperationOutcomeHandler.from_validation_error(e)
            raise OperationOutcomeException(outcome)
