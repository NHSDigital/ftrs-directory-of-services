"""Configuration for ETL ODS CloudWatch metrics.

Derives AWS resource names from ENVIRONMENT and WORKSPACE using
the same Terraform naming conventions as the infrastructure stack.

Resource prefix: ftrs-dos-{env}-etl-ods
Workspace suffix: "" for default, "-{workspace}" otherwise

Usage:
    ENVIRONMENT=dev python scripts/etl_ods/cloudwatch_metrics.py
"""

import os
import sys


class Config:
    """ETL ODS resource naming configuration."""

    PROJECT = "ftrs-dos"
    STACK_NAME = "etl-ods"
    AWS_REGION = os.environ.get("AWS_REGION") or "eu-west-2"
    AWS_PROFILE = os.environ.get("AWS_PROFILE") or ""
    ENVIRONMENT = os.environ.get("ENVIRONMENT") or ""

    @classmethod
    def _get_workspace(cls) -> str:
        return os.environ.get("WORKSPACE") or "default"

    @classmethod
    def _get_workspace_suffix(cls) -> str:
        workspace = cls._get_workspace()
        return f"-{workspace}" if workspace != "default" else ""

    @classmethod
    def get_prefix(cls) -> str:
        """Return the resource prefix: ftrs-dos-{env}-etl-ods."""
        if not cls.ENVIRONMENT:
            print("ERROR: ENVIRONMENT variable is required (dev|test|int|ref)")
            sys.exit(1)
        return f"{cls.PROJECT}-{cls.ENVIRONMENT}-{cls.STACK_NAME}"

    @classmethod
    def get_lambda_functions(cls) -> list[str]:
        """Return Lambda function names for extractor, transformer, consumer."""
        prefix = cls.get_prefix()
        suffix = cls._get_workspace_suffix()
        return [
            f"{prefix}-extractor-lambda{suffix}",
            f"{prefix}-transformer-lambda{suffix}",
            f"{prefix}-consumer-lambda{suffix}",
        ]

    @classmethod
    def get_sqs_queues(cls) -> list[str]:
        """Return SQS queue names (transform and load)."""
        prefix = cls.get_prefix()
        suffix = cls._get_workspace_suffix()
        return [
            f"{prefix}-transform-queue{suffix}",
            f"{prefix}-load-queue{suffix}",
        ]

    @classmethod
    def get_sqs_queue(cls) -> str:
        """Return the transform queue name (primary queue)."""
        return cls.get_sqs_queues()[0]

    @classmethod
    def get_sqs_dlqs(cls) -> list[str]:
        """Return SQS dead-letter queue names."""
        prefix = cls.get_prefix()
        suffix = cls._get_workspace_suffix()
        return [
            f"{prefix}-transform-dlq{suffix}",
            f"{prefix}-load-dlq{suffix}",
        ]

    @classmethod
    def get_eventbridge_rule(cls) -> str:
        """Return the EventBridge Scheduler schedule name."""
        prefix = cls.get_prefix()
        suffix = cls._get_workspace_suffix()
        return f"{prefix}-ods-etl-schedule{suffix}"
