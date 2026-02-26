import pytest
from pytest_bdd import scenarios
from step_definitions.common_steps.data_steps import *  # noqa: F403
from utilities.infra.repo_util import (
    check_record_in_repo,
    model_from_json_file,
)

# Load feature file
scenarios("./infra_features/data_repository.feature")


@pytest.fixture
def organisation_repo_seeded(organisation_repo):
    json_file = "Organisation/organisation-for-session-seeded-repo-test.json"
    organisation = model_from_json_file(json_file, organisation_repo)
    if not check_record_in_repo(organisation_repo, organisation.id):
        organisation_repo.delete(organisation.id)
    organisation_repo.create(organisation)
    yield organisation_repo
    organisation_repo.delete(organisation.id)
