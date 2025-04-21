from pathlib import Path

from pipeline.exceptions import ExtractArgsError
from pipeline.s3_utils.s3_operations import validate_s3_uri


# TODO: consider using kwargs, and dynamically checking based on common names, this could tidy up the function inputs
def validate_paths(
    local_path: Path, s3_uri: str, local_path_name: str, s3_uri_name: str
) -> None:
    if any(
        [
            local_path is None and s3_uri is None,
            local_path is not None and s3_uri is not None,
        ]
    ):
        err_msg = f"Either {local_path_name} or {s3_uri_name} must be provided."
        raise ExtractArgsError(err_msg)

    if s3_uri is not None and not validate_s3_uri(uri=s3_uri):
        err_msg = f"Invalid S3 URI: {s3_uri_name}. Please provide a valid S3 URI and confirm you have access to the S3 bucket."
        raise ExtractArgsError(err_msg)
