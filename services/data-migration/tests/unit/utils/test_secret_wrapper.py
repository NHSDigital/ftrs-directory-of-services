from unittest import mock

import pytest

from pipeline.utils.secret_wrapper import GetSecretWrapper


def test_get_secret_success() -> None:
    mock_client = mock.Mock()
    wrapper = GetSecretWrapper(mock_client)
    secret_name = "my_secret"
    mock_client.get_secret_value.return_value = {"SecretString": "secret_value"}

    result = wrapper.get_secret(secret_name)

    assert result == "secret_value"
    mock_client.get_secret_value.assert_called_once_with(
        SecretId=f"/{wrapper.project_name}/{wrapper.environment}/{secret_name}"
    )


def test_get_secret_resource_not_found() -> None:
    """
    Test that the get_secret method handles ResourceNotFoundException.
    """
    mock_client = mock.Mock()
    mock_client.exceptions.ResourceNotFoundException = Exception
    mock_client.get_secret_value.side_effect = (
        mock_client.exceptions.ResourceNotFoundException
    )

    wrapper = GetSecretWrapper(mock_client)
    secret_name = "nonexistent_secret"

    result = wrapper.get_secret(secret_name)

    assert result == f"The requested secret {secret_name} was not found."
    mock_client.get_secret_value.assert_called_once_with(
        SecretId=f"/{wrapper.project_name}/{wrapper.environment}/{secret_name}"
    )


# TODO: get coverage for the exception on this test
def test_get_secret_unknown_exception() -> None:
    """
    Test that the get_secret method handles unknown exceptions.
    """
    mock_client = mock.Mock()
    mock_client.get_secret_value.side_effect = Exception("Unknown error")

    with pytest.raises(Exception):
        wrapper = GetSecretWrapper(mock_client)
        secret_name = "any_secret"
        result = wrapper.get_secret(secret_name)

        assert result == "An unknown error occurred."
        mock_client.get_secret_value.assert_called_once_with(
            SecretId=f"/{wrapper.project_name}/{wrapper.environment}/{secret_name}"
        )
