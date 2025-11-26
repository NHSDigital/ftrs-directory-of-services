import json
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger

# JSON responses directory
JSON_RESPONSES_DIR = Path(__file__).parent.parent.parent / "json_files" / "ods_api_responses"


class VTLTemplateBuilder:
    """Builds VTL templates for API Gateway mock responses."""

    def __init__(self):
        self.json_responses = self._load_json_responses()

    def _load_json_responses(self) -> Dict[str, Any]:
        """Load all JSON responses from the responses directory."""
        responses = {}
        if not JSON_RESPONSES_DIR.exists():
            logger.warning(f"JSON responses directory not found: {JSON_RESPONSES_DIR}")
            return responses

        for json_file in JSON_RESPONSES_DIR.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    responses[json_file.stem] = json.load(f)
                    logger.debug(f"Loaded JSON response: {json_file.stem}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load JSON response {json_file}: {e}")

        logger.info(f"Loaded {len(responses)} JSON response templates")
        return responses

    def build_ods_vtl_template(self) -> str:
        """
        Build VTL template with date-based scenario routing.
        API key validation is handled by AWS API Gateway.
        """
        template = self._build_template_header()
        template += self._build_scenario_conditions()
        template += self._build_default_response()
        return template

    def _build_template_header(self) -> str:
        """Build the template header with basic setup."""
        return """
## VTL Template for ODS API Mock - Date-based Scenario Routing
## API key validation is handled by AWS API Gateway (apiKeyRequired=true)
#set($lastUpdated = $input.params('_lastUpdated'))

"""

    def _build_scenario_conditions(self) -> str:
        """Build VTL conditions for each test scenario."""
        scenario_map = self._get_scenario_mappings()

        vtl_conditions = []
        for scenario_date, (json_file, status_code, description) in scenario_map.items():
            if json_file not in self.json_responses:
                logger.warning(f"JSON file not found: {json_file}.json")
                continue

            condition = self._build_single_condition(scenario_date, json_file, status_code, description)
            vtl_conditions.append(condition)

        # Build template with all conditions
        template = """## Tests pass specific dates (e.g., "2025-11-01") that map to test scenarios
## Each date maps to a JSON file from tests/json_files/ods_api_responses/

#if(false)
    ## Placeholder - will never match
    {}
"""
        template += "\n".join(vtl_conditions)
        return template

    def _build_single_condition(
        self,
        scenario_date: str,
        json_file: str,
        status_code: int,
        description: str
    ) -> str:
        """Build VTL condition for a single scenario."""
        json_data = json.dumps(self.json_responses[json_file])

        condition = f"""#elseif($lastUpdated == "{scenario_date}")
    ## Scenario: {description}
    ## File: {json_file}.json"""

        if status_code != 200:
            condition += f"\n    #set($context.responseOverride.status = {status_code})"

        condition += f"\n    {json_data}"
        return condition

    def _build_default_response(self) -> str:
        """Build the default response for unmatched scenarios."""
        return """
#else
    ## Default scenario: Return empty bundle with the provided parameter value
    {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 0,
        "link": [{
            "relation": "self",
            "url": "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization?_lastUpdated=$lastUpdated"
        }]
    }
#end
"""

    def _get_scenario_mappings(self) -> Dict[str, tuple]:
        """Get scenario mappings: date -> (json_file, status_code, description)."""
        return {
            "2025-11-01": ("error_empty_payload", 200, "Empty payload - no organizations"),
            "2025-11-02": ("error_invalid_data_types", 200, "Invalid data types - validation test"),
            "2025-11-03": ("error_missing_required_fields", 200, "Missing required fields"),
            "2025-11-04": ("error_extra_unexpected_field", 200, "Extra unexpected fields"),
            "2025-11-05": ("error_invalid_resource", 200, "Invalid resource type"),
            "2025-11-06": ("error_request_too_old_payload", 200, "Request too old"),
            "2025-11-07": ("error_unauthorized", 401, "Unauthorized error"),
            "2025-11-08": ("error_unknown_resource_type", 400, "Unknown resource type"),
            "2025-11-09": ("error_unknown_search_parameter", 400, "Unknown search parameter"),
        }

    def get_loaded_scenarios(self) -> List[str]:
        """Get list of successfully loaded scenario names."""
        return list(self.json_responses.keys())
