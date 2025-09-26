from pytest_bdd import scenarios
from step_definitions.common_steps.data_steps import *  # noqa: F403

# Load feature file
scenarios("./infra_features/data_repository.feature")
