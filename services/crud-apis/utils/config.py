import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    env: str = "local"
    workspace: str | None = None
    endpoint_url: str | None = None

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)
        self.env = os.getenv("ENVIRONMENT", self.env)
        self.workspace = os.getenv("WORKSPACE", self.workspace)
        self.endpoint_url = os.getenv("ENDPOINT_URL", self.endpoint_url)


def get_env_variables() -> Settings:
    return Settings()
