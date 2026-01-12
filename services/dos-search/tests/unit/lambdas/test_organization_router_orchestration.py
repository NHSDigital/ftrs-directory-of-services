from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.bundle import Bundle

from functions.organization_handler import DEFAULT_RESPONSE_HEADERS
from lambdas.organization_get_router.handler import lambda_handler


@pytest.fixture
def lambda_context() -> LambdaContext:
    return MagicMock(spec=LambdaContext)


@pytest.fixture
def apigw_event() -> dict:
    return {
        "path": "/Organization",
        "httpMethod": "GET",
        "headers": {},
        "queryStringParameters": {
            "identifier": "odsOrganisationCode|ABC123",
            "_revinclude": "Endpoint:organization",
        },
        "requestContext": {"requestId": "req-id"},
        "body": None,
    }


class TestOrganizationRouterOrchestration:
    def test_router_inline_mode_uses_ftrs_service(
        self,
        apigw_event: dict,
        lambda_context: LambdaContext,
    ) -> None:
        bundle = Bundle.model_construct(id="bundle-id")

        with (
            patch(
                "functions.organization_handler.get_orchestrator_mode",
                return_value="inline",
            ),
            patch("functions.organization_handler.FtrsService") as mock_service,
        ):
            mock_service.return_value.endpoints_by_ods.return_value = bundle

            response = lambda_handler(apigw_event, lambda_context)

        assert response["statusCode"] == 200
        assert response["multiValueHeaders"] == {
            header: [value] for header, value in DEFAULT_RESPONSE_HEADERS.items()
        }

    def test_router_lambda_mode_invokes_worker(
        self,
        apigw_event: dict,
        lambda_context: LambdaContext,
    ) -> None:
        worker_response = {
            "statusCode": 200,
            "headers": DEFAULT_RESPONSE_HEADERS,
            "body": '{"resourceType":"Bundle"}',
        }

        with (
            patch(
                "functions.organization_handler.get_orchestrator_mode",
                return_value="lambda",
            ),
            patch(
                "functions.organization_handler.get_worker_lambda_names",
                return_value=["org-worker-1"],
            ),
            patch(
                "functions.organization_handler.invoke_lambda_pipeline_json",
                return_value=worker_response,
            ) as mock_invoke,
        ):
            response = lambda_handler(apigw_event, lambda_context)

        mock_invoke.assert_called_once()
        assert response["statusCode"] == 200
        assert response["body"] == worker_response["body"]

    def test_router_lambda_mode_supports_multiple_workers(
        self,
        apigw_event: dict,
        lambda_context: LambdaContext,
    ) -> None:
        final_worker_response = {
            "statusCode": 200,
            "headers": DEFAULT_RESPONSE_HEADERS,
            "body": '{"resourceType":"Bundle","id":"final"}',
        }

        with (
            patch(
                "functions.organization_handler.get_orchestrator_mode",
                return_value="lambda",
            ),
            patch(
                "functions.organization_handler.get_worker_lambda_names",
                return_value=["org-worker-1", "org-worker-2", "org-worker-3"],
            ),
            patch(
                "functions.organization_handler.invoke_lambda_pipeline_json",
                return_value=final_worker_response,
            ) as mock_invoke,
        ):
            response = lambda_handler(apigw_event, lambda_context)

        mock_invoke.assert_called_once()
        assert response["statusCode"] == 200
        assert response["body"] == final_worker_response["body"]
