"""Pytest configuration for CRUD APIs integration tests.

This module provides fixtures for running integration tests against
real DynamoDB tables using LocalStack testcontainers.

Usage:
    Run all tests (unit + integration):
        pytest

    Run only unit tests (no Docker required):
        pytest -m "not integration"

    Run only integration tests:
        pytest -m integration
"""

import os

# Force test environment settings BEFORE importing fixtures
# This ensures consistent table names between fixture setup and app runtime
os.environ["ENVIRONMENT"] = "local"
os.environ.pop("WORKSPACE", None)  # Remove workspace to avoid workspace-specific table names

from ftrs_test_util.fixtures import *  # noqa: F403, E402
from ftrs_test_util.steps import *  # noqa: F403, E402
