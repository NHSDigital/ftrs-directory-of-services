import json

from ftrs_data_layer.models import DBModel
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

JSON_FILES_PATH="tests/json_files/"

def model_from_json_file(json_file: str, model_repo: AttributeLevelRepository) -> DBModel:
    with open(f"{JSON_FILES_PATH}{json_file}", "r") as f:
        model_data = json.load(f)
    return model_repo.model_cls(**model_data)


def save_json_file_from_model(get_model_result):
    json_file = f"{JSON_FILES_PATH}{get_model_result.__class__.__name__}/{str(get_model_result.id)}.json"
    with open(json_file, "w") as f:
        f.write(get_model_result.model_dump_json(indent=2))
