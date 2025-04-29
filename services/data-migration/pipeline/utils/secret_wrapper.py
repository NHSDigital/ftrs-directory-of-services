import logging
import os

from dotenv import load_dotenv


class GetSecretWrapper:
    def __init__(self, secretsmanager_client: any) -> None:
        self.client = secretsmanager_client
        load_dotenv()  # Load environment variables from .env file
        self.project_name = os.getenv("PROJECT_NAME")
        self.environment = os.getenv("ENVIRONMENT")

    def get_secret(self, secret_name: any) -> str:
        """
        Retrieve individual secrets from AWS Secrets Manager using the get_secret_value API.
        :param secret_name: The name of the secret fetched.
        :type secret_name: str
        """
        try:
            print(self.project_name)
            print(self.environment)
            get_secret_value_response = self.client.get_secret_value(
                SecretId=f"/{self.project_name}/{self.environment}/{secret_name}"
            )
            logging.info("Secret retrieved successfully.")
            return get_secret_value_response["SecretString"]
        except self.client.exceptions.ResourceNotFoundException:
            msg = f"The requested secret {secret_name} was not found."
            logging.info(msg)
            return msg
        except Exception as e:
            msg = f"An unknown error occurred: {e}"
            logging.info(msg)
            raise msg
