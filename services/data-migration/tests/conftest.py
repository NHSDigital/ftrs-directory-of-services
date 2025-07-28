import os
from typing import Any

from pydantic._internal._generate_schema import GenerateSchema
from pydantic_core import core_schema

from tests.util.fixtures import *  # noqa: F403

os.environ["ENVIRONMENT"] = "local"
os.environ["WORKSPACE"] = "test_workspace"
os.environ["ENDPOINT_URL"] = "http://localhost:8000"
os.environ["PROJECT_NAME"] = "ftrs-directory-of-services"

initial_match_type = GenerateSchema.match_type


def match_type(self: GenerateSchema, obj: Any) -> Any:  # noqa: ANN401
    if getattr(obj, "__name__", None) == "datetime":
        return core_schema.datetime_schema()
    return initial_match_type(self, obj)


GenerateSchema.match_type = match_type
