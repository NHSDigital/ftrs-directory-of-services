"""Unit tests for S3 fixture helper functions."""

from unittest.mock import MagicMock, call, patch

import pytest


class TestCreateS3Bucket:
    """Tests for create_s3_bucket function."""

    def test_creates_bucket_with_location_constraint(self) -> None:
        """Should create bucket with LocationConstraint for non-us-east-1 regions."""
        from ftrs_common.testing.dynamodb_fixtures import create_s3_bucket

        mock_client = MagicMock()

        result = create_s3_bucket(mock_client, "test-bucket", region="eu-west-2")

        assert result == "test-bucket"
        mock_client.create_bucket.assert_called_once_with(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )

    def test_creates_bucket_without_location_for_us_east_1(self) -> None:
        """Should create bucket without LocationConstraint for us-east-1."""
        from ftrs_common.testing.dynamodb_fixtures import create_s3_bucket

        mock_client = MagicMock()

        result = create_s3_bucket(mock_client, "test-bucket", region="us-east-1")

        assert result == "test-bucket"
        mock_client.create_bucket.assert_called_once_with(Bucket="test-bucket")

    def test_handles_bucket_already_exists(self) -> None:
        """Should handle BucketAlreadyExists exception gracefully."""
        from ftrs_common.testing.dynamodb_fixtures import create_s3_bucket

        mock_client = MagicMock()

        # Create proper exception class that inherits from BaseException
        class BucketAlreadyExists(Exception):
            pass

        class BucketAlreadyOwnedByYou(Exception):
            pass

        mock_client.exceptions.BucketAlreadyExists = BucketAlreadyExists
        mock_client.exceptions.BucketAlreadyOwnedByYou = BucketAlreadyOwnedByYou
        mock_client.create_bucket.side_effect = BucketAlreadyExists("Bucket exists")

        result = create_s3_bucket(mock_client, "existing-bucket")

        assert result == "existing-bucket"

    def test_handles_bucket_already_owned_by_you(self) -> None:
        """Should handle BucketAlreadyOwnedByYou exception gracefully."""
        from ftrs_common.testing.dynamodb_fixtures import create_s3_bucket

        mock_client = MagicMock()

        # Create proper exception classes that inherit from BaseException
        class BucketAlreadyExists(Exception):
            pass

        class BucketAlreadyOwnedByYou(Exception):
            pass

        mock_client.exceptions.BucketAlreadyExists = BucketAlreadyExists
        mock_client.exceptions.BucketAlreadyOwnedByYou = BucketAlreadyOwnedByYou
        mock_client.create_bucket.side_effect = BucketAlreadyOwnedByYou(
            "Bucket owned by you"
        )

        result = create_s3_bucket(mock_client, "my-bucket")

        assert result == "my-bucket"


class TestCleanupS3Bucket:
    """Tests for cleanup_s3_bucket function."""

    def test_deletes_objects_then_bucket(self) -> None:
        """Should delete all objects before deleting the bucket."""
        from ftrs_common.testing.dynamodb_fixtures import cleanup_s3_bucket

        mock_client = MagicMock()
        mock_paginator = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {"Contents": [{"Key": "file1.txt"}, {"Key": "file2.txt"}]}
        ]

        cleanup_s3_bucket(mock_client, "test-bucket")

        # Should delete objects
        mock_client.delete_objects.assert_called()
        # Should delete bucket
        mock_client.delete_bucket.assert_called_once_with(Bucket="test-bucket")

    def test_handles_empty_bucket(self) -> None:
        """Should handle empty bucket without errors."""
        from ftrs_common.testing.dynamodb_fixtures import cleanup_s3_bucket

        mock_client = MagicMock()
        mock_paginator = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{"Contents": []}]

        cleanup_s3_bucket(mock_client, "empty-bucket")

        # Should not call delete_objects for empty bucket
        mock_client.delete_objects.assert_not_called()
        # Should still delete the bucket
        mock_client.delete_bucket.assert_called_once_with(Bucket="empty-bucket")

    def test_handles_nonexistent_bucket(self) -> None:
        """Should handle NoSuchBucket exception gracefully."""
        from ftrs_common.testing.dynamodb_fixtures import cleanup_s3_bucket

        mock_client = MagicMock()
        mock_client.exceptions.NoSuchBucket = Exception
        mock_paginator = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.side_effect = Exception("No such bucket")

        # Should not raise
        cleanup_s3_bucket(mock_client, "nonexistent-bucket")


class TestUploadToS3:
    """Tests for upload_to_s3 function."""

    def test_uploads_bytes_content(self) -> None:
        """Should upload bytes content correctly."""
        from ftrs_common.testing.dynamodb_fixtures import upload_to_s3

        mock_client = MagicMock()

        upload_to_s3(
            mock_client,
            bucket_name="test-bucket",
            key="path/to/file.bin",
            content=b"binary content",
            content_type="application/octet-stream",
        )

        mock_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="path/to/file.bin",
            Body=b"binary content",
            ContentType="application/octet-stream",
        )

    def test_uploads_string_content(self) -> None:
        """Should convert string content to bytes and upload."""
        from ftrs_common.testing.dynamodb_fixtures import upload_to_s3

        mock_client = MagicMock()

        upload_to_s3(
            mock_client,
            bucket_name="test-bucket",
            key="file.txt",
            content="text content",
            content_type="text/plain",
        )

        mock_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="file.txt",
            Body=b"text content",
            ContentType="text/plain",
        )


class TestDownloadFromS3:
    """Tests for download_from_s3 function."""

    def test_downloads_content(self) -> None:
        """Should download and return content as bytes."""
        from ftrs_common.testing.dynamodb_fixtures import download_from_s3

        mock_client = MagicMock()
        mock_body = MagicMock()
        mock_body.read.return_value = b"downloaded content"
        mock_client.get_object.return_value = {"Body": mock_body}

        result = download_from_s3(mock_client, "test-bucket", "file.txt")

        assert result == b"downloaded content"
        mock_client.get_object.assert_called_once_with(
            Bucket="test-bucket", Key="file.txt"
        )


class TestModuleExports:
    """Tests for module exports via __init__.py."""

    def test_s3_fixtures_are_exported(self) -> None:
        """S3 fixtures should be accessible via ftrs_common.testing."""
        from ftrs_common.testing import (
            cleanup_s3_bucket,
            create_s3_bucket,
            download_from_s3,
            s3_bucket,
            s3_bucket_session,
            s3_client,
            s3_resource,
            upload_to_s3,
        )

        # Just verify they're callable/accessible
        assert callable(create_s3_bucket)
        assert callable(cleanup_s3_bucket)
        assert callable(upload_to_s3)
        assert callable(download_from_s3)
        # Fixtures are functions too
        assert callable(s3_client)
        assert callable(s3_resource)
        assert callable(s3_bucket)
        assert callable(s3_bucket_session)
