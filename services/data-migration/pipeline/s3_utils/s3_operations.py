from pipeline.exceptions import InvalidS3URI
from pipeline.s3_utils.s3_bucket_wrapper import BucketWrapper


def validate_s3_uri(uri: str) -> str:
    if not uri.startswith("s3://"):
        raise InvalidS3URI(uri)
    bucket_wrapper = BucketWrapper(uri)
    if bucket_wrapper.s3_bucket_exists():
        return uri
    else:
        return None
