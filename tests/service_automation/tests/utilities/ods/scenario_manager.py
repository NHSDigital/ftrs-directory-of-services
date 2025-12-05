import pytest
from typing import Dict, List


# Scenario-to-date mapping for VTL mock
# Each scenario is mapped to a unique date that the VTL mock recognizes

SCENARIO_DATE_MAP: Dict[str, str] = {
    "empty_payload": "2025-11-01",
    "invalid_data_types": "2025-11-02",
    "missing_required_fields": "2025-11-03",
    "extra_unexpected_field": "2025-11-04",
    "invalid_resource": "2025-11-05",
    "request_too_old": "2025-11-06",
    "unauthorized": "2025-11-07",
    "unknown_resource_type": "2025-11-08",
    "unknown_search_parameter": "2025-11-09",
}


class ScenarioManager:
    """Manages VTL mock test scenarios and their date mappings."""

    @staticmethod
    def get_scenario_date(scenario_name: str) -> str:
        """
        Get the date that triggers a specific scenario in VTL mock.
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
