import pytest
import json
import yaml


@pytest.fixture(scope="module")
def oas_spec():
    spec_name = "openapi.yaml"
    spec_path = "tests/oas_schemas/"
    spec = spec_path + spec_name
    with open(spec, "r") as spec_file:
        return yaml.load(spec_file, Loader=yaml.SafeLoader)

