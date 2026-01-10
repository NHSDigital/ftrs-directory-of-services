import pytest
from typing import Dict, List

SCENARIO_DATE_MAP: Dict[str, str] = {
    "happy_path": "2025-12-08",              # Returns valid Organization with proper structure
    "empty_payload": "2025-12-09",           # Returns bundle with total: 0, no entries
    "invalid_data_types": "2025-12-10",      # Returns Location instead of Organization (wrong resourceType)
    "missing_required_fields": "2025-12-11", # Returns Organization with missing required fields
    "extra_unexpected_field": "2025-12-12",  # Returns Organization with unexpected fields
    "invalid_resource": "2025-12-13",        # Returns Location instead of Organization
    "request_too_old": "2025-12-14",         # Returns empty bundle (total: 0)
    "unauthorized": "2025-12-15",            # Returns 401 unauthorized response
    "server_error": "2025-12-16",            # Returns 500 internal server error
    "unknown_resource_type": "2025-12-17",   # Returns wrong resourceType (Location)
    "unknown_search_parameter": "2025-12-18", # Returns bundle with unknown parameter handling
}


class ScenarioManager:
    """Manages ODS mock test scenarios and their date mappings."""

    @staticmethod
    def get_scenario_date(scenario_name: str) -> str:
        """
        Get the date that triggers a specific scenario in ODS mock.
        """
        if scenario_name not in SCENARIO_DATE_MAP:
            available = ", ".join(SCENARIO_DATE_MAP.keys())
            raise KeyError(f"Unknown scenario '{scenario_name}'. Available: {available}")

        return SCENARIO_DATE_MAP[scenario_name]

    @staticmethod
    def get_all_scenarios() -> Dict[str, str]:
        """Get all available scenarios and their corresponding dates."""
        return SCENARIO_DATE_MAP.copy()

    @staticmethod
    def get_scenario_names() -> List[str]:
        """Get list of all available scenario names."""
        return list(SCENARIO_DATE_MAP.keys())


@pytest.fixture
def ods_empty_payload_scenario() -> str:
    return ScenarioManager.get_scenario_date("empty_payload")


@pytest.fixture
def ods_invalid_data_types_scenario() -> str:
    return ScenarioManager.get_scenario_date("invalid_data_types")


@pytest.fixture
def ods_missing_required_fields_scenario() -> str:
    return ScenarioManager.get_scenario_date("missing_required_fields")


@pytest.fixture
def ods_extra_unexpected_field_scenario() -> str:
    return ScenarioManager.get_scenario_date("extra_unexpected_field")


@pytest.fixture
def ods_invalid_resource_scenario() -> str:
    return ScenarioManager.get_scenario_date("invalid_resource")


@pytest.fixture
def ods_request_too_old_scenario() -> str:
    return ScenarioManager.get_scenario_date("request_too_old")


@pytest.fixture
def ods_unauthorized_scenario() -> str:
    return ScenarioManager.get_scenario_date("unauthorized")


@pytest.fixture
def ods_unknown_resource_type_scenario() -> str:
    return ScenarioManager.get_scenario_date("unknown_resource_type")


@pytest.fixture
def ods_unknown_search_parameter_scenario() -> str:
    return ScenarioManager.get_scenario_date("unknown_search_parameter")


@pytest.fixture
def ods_server_error_scenario() -> str:
    return ScenarioManager.get_scenario_date("server_error")


@pytest.fixture
def ods_happy_path_scenario() -> str:
    return ScenarioManager.get_scenario_date("happy_path")
