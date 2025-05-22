import os

from dotenv import load_dotenv

load_dotenv()


def get_env_variables() -> dict[str, str]:
    return {
        "env": os.getenv("ENVIRONMENT", "local"),
        "workspace": os.getenv("WORKSPACE", None),
        "endpoint_url": os.getenv("ENDPOINT_URL", "http://localhost:8000"),
    }
