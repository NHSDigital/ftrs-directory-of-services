from enum import Enum


class FeatureFlag(str, Enum):
    DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED = (
        "data_migration_search_triage_code_enabled"
    )
