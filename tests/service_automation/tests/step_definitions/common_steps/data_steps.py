import pytest
from utilities.common.config import config
from pytest_bdd import scenarios, given, when, then, parsers
from loguru import logger
from utilities.infra.dynamodb_util import dynamodb

scenarios("./is_infra_features/lambda.feature")


@given("I reset the data by deleting id {id} in the dynamoDB table {resource_name}")
def dynamodb_delete(workspace, id, resource_name):
    table_name = resource_name + workspace
    dynamodb.delete_record_by_id(table_name, id)


@given("I setup the data by inserting from file {file_name} into the dynamoDB table {resource_name}")
def dynamodb_add(context, file_name, resource_name):
    body = config.get("file_name")
    table_name = resource_name + context.workspace
    dynamodb.add_record_from_file(table_name, body)


# @then(parsers.parse("I can retrieve data for id "{id}" in the dynamoDB table"))
# def dynamodb_get(context, id):
#     table_name = context.resource_name + context.workspace
#     response = dynamodb.get_record_by_id(table_name, id)
#     assert response["Item"]["id"].is_equal_to(id)


@then("data for id {id} in the dynamoDB table has been deleted")
def dynamodb_check_delete(context, id):
    table_name = context.resource_name + context.workspace
    response = dynamodb.get_record_by_id(table_name, id)
    assert response["ResponseMetadata"]["HTTPHeaders"]["content-length"] == ("2")
    assert response.does_not_contain("Item")
