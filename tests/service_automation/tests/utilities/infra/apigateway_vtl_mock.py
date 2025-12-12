"""
Mock ODS API using VTL templates.
"""
import time
from typing import Dict, Any, Optional

import boto3
from loguru import logger

from .vtl_template_builder import VTLTemplateBuilder
from .apigateway_manager import APIGatewayManager
from .apikey_manager import APIKeyManager


class APIGatewayVTLMockManager:
    """
    Orchestrates creation of API Gateway mock with VTL templates.
    """

    def __init__(self, region_name: str = "eu-west-2"):
        """Initialize the mock manager with AWS region."""
        self.region_name = region_name
        self.client = boto3.client("apigateway", region_name=region_name)

        # Initialize component managers
        self.vtl_builder = VTLTemplateBuilder()
        self.api_manager = APIGatewayManager(self.client)
        self.key_manager = APIKeyManager(self.client)

        # Track created resources for cleanup
        self.api_id: Optional[str] = None
        self.api_key_id: Optional[str] = None
        self.usage_plan_id: Optional[str] = None
        self.endpoint_url: Optional[str] = None
        self.api_key_value: Optional[str] = None

    def create_and_deploy_mock_api(
        self,
        api_name: str,
        resource_path: str = "Organization",
        api_key_required: bool = True
    ) -> Dict[str, str]:
        """
        Create and deploy a complete mock API with authentication.
        """
        try:
            logger.info(f"Creating mock API: {api_name}")

            # Step 1: Create REST API
            self.api_id = self.api_manager.create_rest_api(api_name)

            # Step 2: Create resource hierarchy for nested paths
            root_resource_id = self.api_manager.get_root_resource_id(self.api_id)

            # Handle nested resource paths by creating each segment
            path_segments = resource_path.split('/')
            current_parent_id = root_resource_id

            for segment in path_segments:
                if segment:  # Skip empty segments from leading/trailing slashes
                    current_parent_id = self.api_manager.create_api_resource(
                        self.api_id, current_parent_id, segment
                    )

            # The final resource_id is where we'll add the method
            resource_id = current_parent_id

            # Step 3: Create GET method with VTL template
            self.api_manager.create_api_method(
                self.api_id, resource_id, "GET", api_key_required
            )

            # Step 4: Create mock integration with VTL template
            vtl_template = self.vtl_builder.build_ods_vtl_template()
            self.api_manager.create_mock_integration(
                self.api_id, resource_id, "GET", vtl_template
            )

            # Step 5: Deploy API
            self.endpoint_url = self.api_manager.deploy_api(self.api_id)

            # Step 6: Set up API key authentication if required
            api_key_value = None
            if api_key_required:
                api_key_value = self._setup_api_authentication(api_name)

            result = {
                "endpoint_url": self.endpoint_url,
                "api_key": api_key_value or ""
            }

            # Final wait to ensure all AWS resources are fully propagated and ready
            logger.info("Waiting for API Gateway resources to fully propagate...")
            time.sleep(5)

            logger.info(f"Mock API created successfully: {self.endpoint_url}")
            return result

        except Exception as e:
            logger.error(f"Failed to create mock API: {e}")
            self.cleanup()
            raise

    def _setup_api_authentication(self, api_name: str) -> str:
        """Set up API key authentication for the API."""
        # Create API key
        self.api_key_id, self.api_key_value = self.key_manager.create_api_key(
            f"{api_name}-key"
        )

        # Create usage plan
        self.usage_plan_id = self.key_manager.create_usage_plan(
            f"{api_name}-plan", self.api_id
        )

        # Associate key with usage plan
        self.key_manager.associate_api_key_with_usage_plan(
            self.usage_plan_id, self.api_key_id
        )

        return self.api_key_value

    def get_mock_details(self) -> Dict[str, Any]:
        """Get details about the created mock API."""
        return {
            "api_id": self.api_id,
            "endpoint_url": self.endpoint_url,
            "api_key_id": self.api_key_id,
            "api_key_value": self.api_key_value,
            "usage_plan_id": self.usage_plan_id,
            "region": self.region_name,
            "loaded_scenarios": self.vtl_builder.get_loaded_scenarios()
        }

    def cleanup(self) -> None:
        """Clean up all created AWS resources."""
        logger.info("Starting cleanup of mock API resources...")

        # Clean up in reverse order of creation
        if self.api_key_id:
            self.key_manager.delete_api_key(self.api_key_id)
            self.api_key_id = None

        if self.usage_plan_id:
            self.key_manager.delete_usage_plan(self.usage_plan_id)
            self.usage_plan_id = None

        if self.api_id:
            self.api_manager.delete_rest_api(self.api_id)
            self.api_id = None

        # Reset state
        self.endpoint_url = None
        self.api_key_value = None

        logger.info("Cleanup completed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.cleanup()
