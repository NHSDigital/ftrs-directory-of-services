from pytest_bdd import scenarios

from step_definitions.data_migration_steps.test_data_migration_address_steps import *  # noqa: F403

scenarios(
    "../../tests/features/data_migration_features/location/service_transformation_address_without_county.feature"
)

