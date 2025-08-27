import json
from loguru import logger

from ftrs_data_layer.domain import DBModel
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

JSON_FILES_PATH = "tests/json_files/"


def model_from_json_file(
    json_file: str, model_repo: AttributeLevelRepository
) -> DBModel:
    with open(f"{JSON_FILES_PATH}{json_file}", "r") as f:
        model_data = json.load(f)
    return model_repo.model_cls(**model_data)


def save_json_file_from_model(get_model_result):
    json_file = f"{JSON_FILES_PATH}{get_model_result.__class__.__name__}/{str(get_model_result.id)}.json"
    with open(json_file, "w") as f:
        f.write(get_model_result.model_dump_json(indent=2))


def check_record_in_repo(model_repo, model_id):
    record = model_repo.get(model_id)
    logger.info(f"Checking if record with ID {model_id} exists in the repository.")
    if record is not None:
        exists = False
        logger.info(f"Record found: {record}")
    else:
        logger.debug(f"Record not found: {model_id}")
        exists = True
    return exists
