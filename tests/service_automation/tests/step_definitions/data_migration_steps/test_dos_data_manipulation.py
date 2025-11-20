"""BDD steps for manipulating DoS source database data."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Type

import pytest
from pytest_bdd import given, when, then, parsers, scenarios
from sqlalchemy.orm import Session
from sqlmodel import select

from ftrs_data_layer.domain import legacy as legacy_model
from utilities.common.legacy_dos_rds_tables import TABLE_TO_ENTITY
from utilities.common.constants import STRING_FIELDS
from step_definitions.data_migration_steps.dos_data_manipulation_steps import *  # noqa: F403

# Load scenarios from feature files
scenarios("../../tests/features/data_migration_features/dos_data_manipulation.feature")
