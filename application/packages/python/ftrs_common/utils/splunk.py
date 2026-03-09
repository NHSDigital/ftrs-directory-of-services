import os

SPLUNK_INDEX_PREFIX = "app_directoryofservices"
_DEV_ENVIRONMENTS = {"dev", "test"}


def get_splunk_index() -> str:
    """
    Return the Splunk HEC index name for the current environment.

    Resolves to 'dev' when:
      - The ENVIRONMENT env var is absent or empty
      - ENVIRONMENT is 'dev' or 'test'
      - The WORKSPACE env var is present and non-empty (workspace environment)

    In all other cases, the resolved environment matches the ENVIRONMENT value.
    """
    environment = os.environ.get("ENVIRONMENT") or ""
    workspace = os.environ.get("WORKSPACE") or ""

    if not environment or environment in _DEV_ENVIRONMENTS or workspace:
        resolved_env = "dev"
    else:
        resolved_env = environment

    return f"{SPLUNK_INDEX_PREFIX}_{resolved_env}"
