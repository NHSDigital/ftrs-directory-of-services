"""
API Gateway REST API Manager for creating and configuring mock APIs.

Handles the AWS API Gateway REST API creation, resource management, and deployment.
"""
import time
from loguru import logger

# Constants
APPLICATION_JSON = 'application/json'


class APIGatewayManager:
    """Manages API Gateway REST APIs for mock testing."""

    def __init__(self, api_gateway_client):
        self.client = api_gateway_client

    def create_rest_api(self, api_name: str) -> str:
        """Create a REST API and return its ID."""
        try:
            response = self.client.create_rest_api(
                name=api_name,
                description=f'Mock API for {api_name}',
                endpointConfiguration={'types': ['REGIONAL']}
            )
            api_id = response['id']
            logger.info(f"Created REST API: {api_name} (ID: {api_id})")
            return api_id

        except Exception as e:
            logger.error(f"Failed to create REST API {api_name}: {e}")
            raise

    def create_api_resource(self, api_id: str, parent_resource_id: str, path: str) -> str:
        """Create API resource and return its ID."""
        try:
            response = self.client.create_resource(
                restApiId=api_id,
                parentId=parent_resource_id,
                pathPart=path
            )
            resource_id = response['id']
            logger.info(f"Created resource: /{path} (ID: {resource_id})")
            return resource_id

        except Exception as e:
            logger.error(f"Failed to create resource /{path}: {e}")
            raise

    def create_api_method(
        self,
        api_id: str,
        resource_id: str,
        http_method: str,
        api_key_required: bool = True
    ) -> None:
        """Create API method with optional API key requirement."""
        try:
            self.client.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                authorizationType='NONE',
                apiKeyRequired=api_key_required,
                requestParameters={'method.request.querystring._lastUpdated': False}
            )
            logger.info(f"Created method: {http_method} (API Key Required: {api_key_required})")

        except Exception as e:
            logger.error(f"Failed to create method {http_method}: {e}")
            raise

    def create_mock_integration(
        self,
        api_id: str,
        resource_id: str,
        http_method: str,
        vtl_template: str
    ) -> None:
        """Create mock integration with VTL template."""
        try:
            # Step 1: Create method response (must be created before integration response)
            self.client.put_method_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                statusCode='200',
                responseModels={APPLICATION_JSON: 'Empty'},
                responseParameters={
                    'method.response.header.Content-Type': True,
                    'method.response.header.Access-Control-Allow-Origin': True
                }
            )

            # Step 2: Create integration
            self.client.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                type='MOCK',
                requestTemplates={APPLICATION_JSON: '{"statusCode": 200}'}
            )

            # Step 3: Create integration response with VTL template
            self.client.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                statusCode='200',
                responseTemplates={APPLICATION_JSON: vtl_template},
                responseParameters={
                    'method.response.header.Content-Type': f"'{APPLICATION_JSON}'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )

            logger.info(f"Created mock integration for {http_method}")

        except Exception as e:
            logger.error(f"Failed to create mock integration for {http_method}: {e}")
            raise

    def get_root_resource_id(self, api_id: str) -> str:
        """Get the root resource ID for an API."""
        try:
            response = self.client.get_resources(restApiId=api_id)
            for resource in response['items']:
                if resource['path'] == '/':
                    return resource['id']
            raise ValueError("Root resource not found")

        except Exception as e:
            logger.error(f"Failed to get root resource ID: {e}")
            raise

    def deploy_api(self, api_id: str, stage_name: str = 'test') -> str:
        """Deploy API to a stage and return the endpoint URL."""
        try:
            self.client.create_deployment(
                restApiId=api_id,
                stageName=stage_name
            )

            # Wait for deployment to be ready - increased delay for API Gateway propagation
            time.sleep(5)

            endpoint_url = f'https://{api_id}.execute-api.eu-west-2.amazonaws.com/{stage_name}'
            logger.info(f"Deployed API to: {endpoint_url}")
            return endpoint_url

        except Exception as e:
            logger.error(f"Failed to deploy API: {e}")
            raise

    def delete_rest_api(self, api_id: str) -> None:
        """Delete a REST API."""
        try:
            self.client.delete_rest_api(restApiId=api_id)
            logger.info(f"Deleted REST API: {api_id}")

        except Exception as e:
            logger.error(f"Failed to delete REST API {api_id}: {e}")
            # Don't re-raise - cleanup should continue
