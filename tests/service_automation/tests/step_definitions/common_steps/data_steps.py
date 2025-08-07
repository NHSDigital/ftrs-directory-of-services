import pytest
from ftrs_data_layer.domain import DBModel, Organisation
from ftrs_data_layer.repository.base import ModelType
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from pytest_bdd import given, parsers, then, when
from utilities.infra.repo_util import model_from_json_file, save_json_file_from_model


@given(parsers.parse("I have a {repo_name} repo"), target_fixture="model_repo")
def get_repo_fixture(
    request: pytest.FixtureRequest, repo_name: str
) -> AttributeLevelRepository:
    repo_fixture_name = f"{repo_name}_repo"
    repo: AttributeLevelRepository = request.getfixturevalue(repo_fixture_name)
    return repo


@given(
    parsers.parse("I have a {repo_name} repo that is seeded"),
    target_fixture="model_repo",
)
def get_repo_fixture(
    request: pytest.FixtureRequest, repo_name: str
) -> AttributeLevelRepository:
    repo_fixture_name = f"{repo_name}_repo_seeded"
    repo: AttributeLevelRepository = request.getfixturevalue(repo_fixture_name)
    return repo


@given(parsers.parse('I create a model in the repo from json file "{json_file}"'))
def create_model_from_json(model_repo: AttributeLevelRepository, json_file: str):
    model = model_from_json_file(json_file, model_repo)
    model_repo.create(model)
    yield
    model_repo.delete(model.id)


@when(
    parsers.parse('I get a model with id "{model_id}" from the repo'),
    target_fixture="get_model_result",
)
def get_from_repo(
    model_repo: AttributeLevelRepository, model_id: str
) -> ModelType | None:
    return model_repo.get(model_id)


@when(
    parsers.parse('I get a model with ODS code "{ods_code}" from the repo'),
    target_fixture="get_model_result",
)
def get_from_repo(
    model_repo: AttributeLevelRepository, ods_code: str
) -> ModelType | None:
    return model_repo.get_first_record_by_ods_code(ods_code)


@then(parsers.parse("a model of type {model_type} is returned"))
def item_is_of_type(get_model_result: DBModel | None, model_type: str):
    assert get_model_result.__class__.__name__ == model_type


@then(parsers.parse('the model has an id of "{model_id}"'))
def model_has_id(get_model_result: DBModel | None, model_id: str):
    assert str(get_model_result.id) == model_id


@then("the model is not returned")
def model_not_exists(get_model_result: Organisation | None):
    assert get_model_result is None


@then("I save the model as a json file")
def save_model_as_json(get_model_result: DBModel):
    save_json_file_from_model(get_model_result)
