import io
import logging
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError


class BucketWrapper:
    """Encapsulates S3 bucket actions."""

    def __init__(self, s3_uri: str) -> None:
        """
        :param s3_uri: S3 bucket URI in the form s3://bucket-name/path/to/object
        """
        s3_uri_parsed = urlparse(s3_uri, allow_fragments=False)
        self.bucket_name = s3_uri_parsed.netloc
        self.bucket_key = s3_uri_parsed.path.lstrip("/")
        self.s3_client = boto3.client("s3")

    def s3_bucket_exists(self) -> bool:
        """
        Determine whether the bucket exists and you have access to it.

        :return: True if the bucket exists; otherwise, False.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            logging.warning(
                "Bucket %s doesn't exist or you don't have access to it.",
                self.bucket_name,
            )
            return False
        else:
            logging.info(
                "Bucket %s exists and you have access to it.", self.bucket_name
            )
            return True

    def s3_put_object(self, data_buffer: bytes) -> None:
        """
        Upload a file to an S3 bucket.

        :param data_buffer: Bytes buffer to upload.
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=self.bucket_key,
                Body=data_buffer,
            )
        except ClientError:
            logging.exception(
                "Failed to put object %s to bucket %s",
                self.bucket_key,
                self.bucket_name,
            )

    def s3_get_object(self) -> bytes | None:
        """
        Download a file from an S3 bucket.

        :return: Bytes buffer of the downloaded file, or None if an error occurs.
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=self.bucket_key
            )
            return response["Body"].read()
        except ClientError:
            logging.exception(
                "Failed to get object %s from bucket %s",
                self.bucket_key,
                self.bucket_name,
            )
            return None

    def s3_delete_object(self) -> None:
        """
        Delete a file from an S3 bucket.
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=self.bucket_key)
            logging.info(
                "Deleted object %s from bucket %s", self.bucket_key, self.bucket_name
            )
        except ClientError:
            logging.exception(
                "Failed to delete object %s from bucket %s",
                self.bucket_key,
                self.bucket_name,
            )

    def s3_upload_file(self, buffer: io.BytesIO, file_name: str) -> None:
        """
        Upload a file to an S3 bucket.

        :param buffer: In-memory buffer containing the file data.
        :param file_name: Name of the file to upload.
        """
        try:
            self.s3_client.upload_fileobj(
                buffer,
                Bucket=self.bucket_name,
                Key=f"{self.bucket_key}/{file_name}",
            )
            logging.info("Uploaded file %s to bucket %s", file_name, self.bucket_name)
        except ClientError:
            logging.exception(
                "Failed to upload file %s to bucket %s",
                file_name,
                self.bucket_name,
            )
