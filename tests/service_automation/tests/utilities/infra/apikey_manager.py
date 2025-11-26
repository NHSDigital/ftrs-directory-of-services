"""
API Key and Usage Plan Manager for API Gateway authentication.

Handles creation and management of API keys and usage plans for mock testing.
"""
import time
from typing import Optional, Tuple
from loguru import logger


class APIKeyManager:
    """Manages API keys and usage plans for API Gateway."""

    def __init__(self, api_gateway_client):
        self.client = api_gateway_client

    def create_api_key(self, key_name: str) -> Tuple[str, str]:
        """Create API key and return (key_id, key_value)."""
        try:
            response = self.client.create_api_key(
                name=key_name,
                description=f'API key for {key_name}',
                enabled=True
            )

            key_id = response['id']
            key_value = response['value']
            logger.info(f"Created API key: {key_name} (ID: {key_id})")
            return key_id, key_value

        except Exception as e:
            logger.error(f"Failed to create API key {key_name}: {e}")
            raise

    def create_usage_plan(self, plan_name: str, api_id: str, stage_name: str = 'test') -> str:
        """Create usage plan and return its ID."""
        try:
            response = self.client.create_usage_plan(
                name=plan_name,
                description=f'Usage plan for {plan_name}',
                apiStages=[{
                    'apiId': api_id,
                    'stage': stage_name
                }],
                quota={'limit': 1000, 'period': 'DAY'},
                throttle={'rateLimit': 10, 'burstLimit': 20}
            )

            plan_id = response['id']
            logger.info(f"Created usage plan: {plan_name} (ID: {plan_id})")
            return plan_id

        except Exception as e:
            logger.error(f"Failed to create usage plan {plan_name}: {e}")
            raise

    def associate_api_key_with_usage_plan(self, usage_plan_id: str, api_key_id: str) -> None:
        """Associate API key with usage plan."""
        try:
            self.client.create_usage_plan_key(
                usagePlanId=usage_plan_id,
                keyId=api_key_id,
                keyType='API_KEY'
            )
            logger.info(f"Associated API key {api_key_id} with usage plan {usage_plan_id}")

            # Wait for API key association to propagate across AWS infrastructure
            time.sleep(3)

        except Exception as e:
            logger.error(f"Failed to associate API key with usage plan: {e}")
            raise

    def delete_api_key(self, api_key_id: str) -> None:
        """Delete an API key."""
        try:
            self.client.delete_api_key(apiKey=api_key_id)
            logger.info(f"Deleted API key: {api_key_id}")

        except Exception as e:
            logger.error(f"Failed to delete API key {api_key_id}: {e}")
            # Don't re-raise - cleanup should continue

    def delete_usage_plan(self, usage_plan_id: str) -> None:
        """Delete a usage plan."""
        try:
            self.client.delete_usage_plan(usagePlanId=usage_plan_id)
            logger.info(f"Deleted usage plan: {usage_plan_id}")

        except Exception as e:
            logger.error(f"Failed to delete usage plan {usage_plan_id}: {e}")
            # Don't re-raise - cleanup should continue
