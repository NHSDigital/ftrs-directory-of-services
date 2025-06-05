import pytest
from utilities.common.config import config
from pytest_bdd import scenarios, given, when, then, parsers
from loguru import logger
from utilities.infra import dynamodb_util

scenarios("./is_infra_features/lambda.feature")

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
