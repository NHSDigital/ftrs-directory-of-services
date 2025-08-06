from pytest_bdd import scenarios
from step_definitions.common_steps.data_steps import *  # noqa: F403

# Load feature file
scenarios("./is_infra_features/data_repository.feature")
