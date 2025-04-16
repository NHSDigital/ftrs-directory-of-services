import json

import boto3

from pipeline.db_utils.database_config import DatabaseConfig
from pipeline.extract import extract
from pipeline.secret_utils.secret_wrapper import GetSecretWrapper


def lambda_handler(event: any, context: any) -> dict[str, any] | None:
    """
    AWS Lambda handler function.

    Parameters:
    - event: dict, contains the event data passed to the function.
    - context: object, provides runtime information to the handler.

    Returns:
    - dict: Response object with status code and body.
    """
    try:
        # Log the incoming event
        print("Received event:", json.dumps(event))
        # Extract the database details from the secret manager
        # Retrieve the secret by name
        client = boto3.client("secretsmanager")
        wrapper = GetSecretWrapper(client)
        db_credentials = wrapper.get_secret(DatabaseConfig.SOURCE_DB_CREDENTIALS)
        db_credentials_dict = json.loads(db_credentials)
        # Create a DatabaseConfig object with the retrieved details
        db_config = DatabaseConfig(
            host=db_credentials_dict["host"],
            port=db_credentials_dict["port"],
            user=db_credentials_dict["username"],
            password=db_credentials_dict["password"],
            db_name=db_credentials_dict["dbname"],
        )
        extract(db_config.getDBuri(), output_path="output_path")

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"}),
        }
