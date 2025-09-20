import pytest
from ftrs_data_layer.domain import DBModel, Organisation
from ftrs_data_layer.repository.base import ModelType
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from pytest_bdd import given, parsers, then, when
from utilities.infra.repo_util import model_from_json_file, save_json_file_from_model, check_record_in_repo
from utilities.common.context import Context
from loguru import logger
import uuid


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
    if not check_record_in_repo(model_repo, model.id):
        model_repo.delete(model.id)
    model_repo.create(model)
    yield
    model_repo.delete(model.id)

@when(
    parsers.parse('I get a record with id "{model_id}" from the repo'),
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

def _create_model(model_repo, json_file, ods_code):
    """Helper to create and return a model with unique ID and ODS code."""
    model = model_from_json_file(json_file, model_repo)
    original_code = getattr(model, "identifier_ODS_ODSCode", None)
    if hasattr(model, "identifier_ODS_ODSCode"):
        model.identifier_ODS_ODSCode = ods_code
        logger.info(f"Replacing ODS code '{original_code}' with '{ods_code}'")
    # Assign unique ID
    model.id = str(uuid.uuid4())
    # Ensure repo is clean
    if not check_record_in_repo(model_repo, model.id):
        model_repo.delete(model.id)
    # Save
    model_repo.create(model)
    logger.info(f"Created model ID={model.id}, ODS={model.identifier_ODS_ODSCode}")
    return model


@given(parsers.parse('I create a model in the repo from json file "{json_file}" using specific ODS codes'))
def create_model_from_json_with_specificods(model_repo: AttributeLevelRepository, json_file: str, context: Context):
    """
    Create a model from JSON file, update its ODS code from context, and save to repo temporarily.
    """
    model = _create_model(model_repo, json_file, context.ods_codes[0])
    context.saved_models[model.id] = model
    yield
    logger.info(f"Deleting model ID={model.id}, ODS={model.identifier_ODS_ODSCode}")
    model_repo.delete(model.id)
    context.saved_models.clear()
    logger.info("Single model cleanup complete")



@given(parsers.parse('I create {count:d} models in the repo from json file "{json_file}" using context ODS codes'))
def create_models_from_json(model_repo: AttributeLevelRepository, json_file: str, context: Context, count: int = 10):
    """
    Create multiple models from a JSON file, assign ODS codes from context, generate UUIDs, save to repo, and cleanup after test.
    Only works if the number of context.ods_codes matches the required count.
    """
    if not context.ods_codes or len(context.ods_codes) != count:
        raise AssertionError(
            f"Expected {count} ODS codes, got {len(context.ods_codes) if context.ods_codes else 0}"
        )
    created_models = []
    for i in range(count):
        model = _create_model(model_repo, json_file, context.ods_codes[i])
        context.saved_models[model.id] = model
        created_models.append(model)
    yield
    for model in created_models:
        logger.info(f"Deleting model ID={model.id}, ODS={model.identifier_ODS_ODSCode}")
        model_repo.delete(model.id)
        context.saved_models.clear()
        logger.info("All temporary models deleted and context.saved_models cleared")
