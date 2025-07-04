from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from pydantic import ValidationError

from functions import error_util
from functions.ftrs_service.ftrs_service import FtrsService
from functions.organization_query_params import OrganizationQueryParams

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


@app.get("/organization")
@tracer.capture_method
def get_organization() -> Response:
    try:
        query_params = app.current_event.query_string_parameters or {}
        validated_params = OrganizationQueryParams.model_validate(query_params)

        ods_code = validated_params.ods_code
        logger.append_keys(ods_code=ods_code)

        ftrs_service = FtrsService()
        fhir_resource = ftrs_service.endpoints_by_ods(ods_code)

    except ValidationError as exception:
        logger.warning(
            "Validation error occurred", extra={"validation_errors": exception.errors()}
        )
        fhir_resource = error_util.create_resource_validation_error(exception)
        return create_response(422, fhir_resource)
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
