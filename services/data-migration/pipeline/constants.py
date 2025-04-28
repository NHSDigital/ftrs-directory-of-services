from enum import StrEnum


class TargetEnvironment(StrEnum):
    local = "local"
    dev = "dev"


class Constants:
    # TODO: Remove once load is updated
    GP_PRACTICE_TRANSFORM = "dos-gp-practice-transform"
    GP_PRACTICE_TRANSFORM_FILE = f"{GP_PRACTICE_TRANSFORM}.parquet"
