from enum import Enum
from typing import Self

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pydantic import BaseModel, Field, ValidationError, model_validator
import logging
from fhir.resources.R4B.organization import Organization
from fhir.resources.exceptions import FHIRValidationError

ods_processor_logger = Logger.get(service="ods_processor")


def validate_fhir_organization(payload: dict) -> Organization:
    """
    Validates a FHIR Organization using fhir.resources.
    """
    try:
        return Organization.parse_obj(payload)
    except FHIRValidationError as e:
        logger.warning(f"FHIR Organization validation failed: {e}")
        raise
