import pytest
from utilities.common.config import config
from pytest_bdd import scenarios, given, when, then, parsers
from loguru import logger
from utilities.infra import dynamodb_util

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


@then(parsers.parse('I can retrieve data for id "{id}" in the dynamoDB table "{table_name}"'))
def dynamodb_get( project, workspace, env, id, table_name):
    stack = "database"
    dynamo_table_name = dynamodb_util.get_dynamo_name(project, workspace, env, stack, table_name)
    response = dynamodb_util.get_record_by_id(dynamo_table_name, id)
    assert response["Items"][0]["id"] == id



@then(parsers.parse('the data for id "{id}" in the dynamoDB table "{table_name}" has been deleted'))
def dynamodb_check_delete( project, workspace, env, id, table_name):
    stack = "database"
    dynamo_table_name = dynamodb_util.get_dynamo_name(project, workspace, env, stack, table_name)
    response = dynamodb_util.get_record_by_id(dynamo_table_name, id)
    assert response["Items"] == ([])
    assert response != ("id")
