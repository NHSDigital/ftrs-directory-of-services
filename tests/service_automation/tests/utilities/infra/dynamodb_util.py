import json
import boto3
from loguru import logger
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource("dynamodb")


def get_record_by_id(tablename, id):
    table = dynamodb.Table(tablename)
    # response = table.get_item(Key={"id": id})
    response = table.query(
        KeyConditionExpression=Key('id').eq(id)
    )
    logger.debug(f"Retrieved item with id {id} from table {tablename}: {response}")
    return response


def add_record(tablename, item):
    table = dynamodb.Table(tablename)
    response = table.put_item(Item=item, TableName=tablename)
    return response


def add_record_from_file(tablename, file_name):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
    table = dynamodb.Table(tablename)
    response = table.put_item(Item=json_data, TableName=tablename)
    return response


def delete_record_by_id(tablename, id):
    table = dynamodb.Table(tablename)
    response = table.delete_item(Key={"id": id})
    return response


def get_dynamo_name(project, workspace, env, stack, table_name):
    logger.debug(f"project: {project},  table_name: {table_name}, stack: {stack}, env: {env}, workspace: {workspace}")
    if workspace == "default":
        table_name = project + "-" + env + "-" + stack + "-" + table_name
    else:
        table_name = project + "-" + env + "-" + stack + "-" + table_name + "-" + workspace
    logger.debug("dynamo table name {}", table_name)
    return table_name
