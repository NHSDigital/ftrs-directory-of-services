from pytest_bdd import scenarios

# Import common steps
from step_definitions.common_steps.data_steps import *  # noqa: F403

# Import data migration steps from split files
from step_definitions.data_migration_steps.dos_data_manipulation_steps import *  # noqa: F403
from step_definitions.data_migration_steps.migration_execution_steps import *  # noqa: F403
from step_definitions.data_migration_steps.migration_verification_steps import *  # noqa: F403
from step_definitions.data_migration_steps.migration_state_steps import *  # noqa: F403
from step_definitions.data_migration_steps.dynamodb_verification_steps import *  # noqa: F403
from step_definitions.data_migration_steps.entity_verification_steps import *  # noqa: F403
from step_definitions.data_migration_steps.test_data_migration_address_steps import *  # noqa: F403


scenarios(
    "../features/data_migration_features/gp_practice_migration_happy_path.feature",
    "../features/data_migration_features/gp_enhanced_access_happy_path.feature",
    "../features/data_migration_features/age_range_transformation.feature",
    "../features/data_migration_features/sgsd_transformation.feature",
    "../features/data_migration_features/position_gcs_transformation.feature",
    "../features/data_migration_features/triage_code_migration.feature",
    "../features/data_migration_features/endpoints_transformation.feature",
    "../features/data_migration_features/dispositions_transformation.feature",
    "../features/data_migration_features/opening_times_transformation.feature",
    "../features/data_migration_features/phone_transformation.feature",
    "../features/data_migration_features/email_transformation.feature",
    "../features/data_migration_features/service_migration_validation_failures.feature",
    "../features/data_migration_features/service_migration_state.feature",
    "../features/data_migration_features/number_formatter_transformation.feature",
    "../features/data_migration_features/organisation_transformation.feature",
)

scenarios(
    "../../tests/features/data_migration_features/location/service_transformation_address.feature"
)
