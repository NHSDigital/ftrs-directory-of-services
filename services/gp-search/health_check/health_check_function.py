from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import Organisation
from mypy_boto3_dynamodb import DynamoDBServiceResource

app = APIGatewayRestResolver()


@app.get("/_status")
def get_status() -> Response:
    table_active = _is_table_active()
    status_code = 200 if table_active else 500
    return Response(status_code=status_code)


def _is_table_active() -> bool:
    try:
        repository = get_service_repository(Organisation, "organisation")
        table: DynamoDBServiceResource.Table = repository.table
        table_status: str = table.table_status
    except Exception:
        return False
    else:
        return table_status == "ACTIVE"


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
