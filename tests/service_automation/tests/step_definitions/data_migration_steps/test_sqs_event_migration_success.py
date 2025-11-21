from pytest_bdd import scenarios

from step_definitions.common_steps.data_migration_steps import *  # noqa: F403

scenarios(
    "../../tests/features/data_migration_features/sqs_event_migration_success.feature"
)
