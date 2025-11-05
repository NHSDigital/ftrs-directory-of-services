from typing import Optional

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from pydantic import ValidationError

from . import error_util
from .ftrs_service.ftrs_service import FtrsService
from .organization_query_params import OrganizationQueryParams

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


class ForcedInternalError(Exception):
    """Explicit exception used to deliberately exercise 5xx paths in lower environments."""

    _DEFAULT_MESSAGE = "Forced internal error for testing"

    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or self._DEFAULT_MESSAGE)


def _raise_forced_internal_error() -> None:
    """Helper to raise a controlled internal error (satisfies TRY301 to abstract raise)."""
    raise ForcedInternalError()


@app.get("/Organization")
@tracer.capture_method
def get_organization() -> Response:
    try:
        query_params = app.current_event.query_string_parameters or {}

        # Provide a way to force a 500 to exercise gateway 5xx behaviour in lower envs
        if str(query_params.get("force_error", "")).lower() in ("1", "true", "yes"):  # noqa: SIM103
            _raise_forced_internal_error()

        validated_params = OrganizationQueryParams.model_validate(query_params)

        ods_code = validated_params.ods_code
        logger.append_keys(ods_code=ods_code)

        ftrs_service = FtrsService()
        fhir_resource = ftrs_service.endpoints_by_ods(ods_code)

    except ValidationError as exception:
        logger.warning(
            "Validation error occurred", extra={"validation_errors": exception.errors()}
        )
        fhir_resource = error_util.create_validation_error_operation_outcome(exception)
        return create_response(400, fhir_resource)
    except Exception:
        logger.exception("Internal server error occurred")
        fhir_resource = error_util.create_resource_internal_server_error()
        return create_response(500, fhir_resource)
    else:
        logger.info("Successfully processed")
        return create_response(200, fhir_resource)


def create_response(status_code: int, fhir_resource: FHIRResourceModel) -> Response:
    logger.info("Creating response", extra={"status_code": status_code})
    return Response(
        status_code=status_code,
        content_type="application/fhir+json",
        body=fhir_resource.model_dump_json(),
    )


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
    log_event=True,
    clear_state=True,
)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
