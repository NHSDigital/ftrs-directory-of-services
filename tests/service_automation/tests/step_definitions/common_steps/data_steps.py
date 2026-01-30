import random
import string
from uuid import uuid4

import pytest
from ftrs_data_layer.domain import DBModel, Organisation
from ftrs_data_layer.repository.base import ModelType
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from loguru import logger
from pytest_bdd import given, parsers, then, when
from utilities.common.context import Context
from utilities.infra.repo_util import (
    check_record_in_repo,
    model_from_json_file,
    save_json_file_from_model,
)


def generate_ods_code(length: int) -> str:
    """
    Generate an alphanumeric ODS code (matches ^[A-Za-z0-9]{1,12}$)
    """
    if length < 1 or length > 12:
        raise ValueError("ODS code length must be between 1 and 12")

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


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


@given(
    parsers.parse(
        'I create a model in the repo from json file "{json_file}" using specific ODS codes'
    )
)
def create_model_from_json_with_specific_ods(
    model_repo: AttributeLevelRepository, json_file: str, context: Context
):
    """
    Create a model from JSON file, update its ODS code from context, and save to repo temporarily.
    """
    model = model_from_json_file(json_file, model_repo)
    if hasattr(model, "identifier_ODS_ODSCode"):
        original_code = model.identifier_ODS_ODSCode
        model.identifier_ODS_ODSCode = context.ods_codes[0]
        logger.info(
            f"Replacing ODS code '{original_code}' with '{context.ods_codes[0]}'"
        )
    model.id = str(uuid4())
    if check_record_in_repo(model_repo, model.id):
        model_repo.delete(model.id)
    model_repo.create(model)
    logger.info(f"Created model ID={model.id}, ODS={model.identifier_ODS_ODSCode}")
    context.saved_models[model.id] = model
    yield
    logger.info(f"Deleting model ID={model.id}, ODS={model.identifier_ODS_ODSCode}")
    model_repo.delete(model.id)
    context.saved_models.clear()
    logger.info("Single model cleanup complete")


@given(
    parsers.parse(
        'I create a model in the repo from json file "{json_file}" with specific id'
    ),
    target_fixture="seeded_model",
)
def create_model_from_json_with_specific_id(
    model_repo: AttributeLevelRepository, json_file: str
):
    """
    Create a model from JSON file with dynamic id and ods code.
    """
    model = model_from_json_file(json_file, model_repo)
    # Generate unique ID and ODS code
    model.id = uuid4()
    unique_ods = generate_ods_code(6)
    model.identifier_ODS_ODSCode = unique_ods
    logger.info(f"Generated model ID: {model.id}")
    logger.info(f"Generated ODS code: {unique_ods}")
    if not check_record_in_repo(model_repo, model.id):
        logger.warning(f"Existing record found for ID {model.id}, deleting it")
        model_repo.delete(model.id)
    model_repo.create(model)
    logger.info(f"Organisation seeded successfully with ID {model.id}")
    yield model
    logger.info(f"Cleaning up organisation with ID {model.id}")
    model_repo.delete(model.id)
