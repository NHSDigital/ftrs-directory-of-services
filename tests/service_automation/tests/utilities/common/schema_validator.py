import pytest
import json


@pytest.fixture(scope="module")
def oas_spec():
    spec_name = "openapi.json"
    spec_path = "tests/oas_schemas/json/"
    spec = spec_path + spec_name
    with open(spec, "r") as spec_file:
        return json.load(spec_file)
