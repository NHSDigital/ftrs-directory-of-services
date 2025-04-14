import pytest
from pytest_mock import MockerFixture
from pipeline.cleardown import cleardown, ClearableEntityTypes, _get_entity_cls
from pipeline.common import TargetEnvironment
from typer import Abort
from ftrs_data_layer.models import Organisation, HealthcareService, Location
from unittest.mock import MagicMock


def test_cleardown_invalid_environment() -> None:
    with pytest.raises(
        ValueError,
        match="Invalid environment: prod. Only 'dev' and 'local' are allowed.",
    ):
        cleardown(env="prod")


def test_cleardown_user_aborts(mocker: MockerFixture) -> None:
    mock_confirm = mocker.patch("pipeline.cleardown.confirm", side_effect=Abort)

    with pytest.raises(Abort):
        cleardown(env=TargetEnvironment.dev)

    mock_confirm.assert_called_once_with(
        "Are you sure you want to clear the dev environment? This action cannot be undone.",
        abort=True,
    )


def test_cleardown_user_aborts_with_exception(mocker: MockerFixture) -> None:
    mocker.patch("pipeline.cleardown.confirm", side_effect=Abort())

    with pytest.raises(Abort):
        cleardown(env=TargetEnvironment.dev)


def test_cleardown_success(mocker: MockerFixture) -> None:
    mock_confirm = mocker.patch("pipeline.cleardown.confirm", return_value=True)
    mocker.patch("pipeline.cleardown.track", side_effect=lambda x, description: x)
    mock_repository = mocker.patch("pipeline.cleardown.DocumentLevelRepository")

    mock_records: list[MagicMock] = [
        mocker.MagicMock(id="item1"),
        mocker.MagicMock(id="item2"),
    ]

    mock_repo_instance = mocker.MagicMock()
    mock_repo_instance.iter_records.return_value = mock_records
    mock_repository.return_value = mock_repo_instance

    cleardown(
        env=TargetEnvironment.dev,
        workspace="test-workspace",
        endpoint_url="http://localhost:8000",
        entity_type=[ClearableEntityTypes.organisation],
    )

    mock_confirm.assert_called_once()
    mock_repository.assert_called_once_with(
        table_name="ftrs-dos-db-dev-organisation-test-workspace",
        model_cls=Organisation,
        endpoint_url="http://localhost:8000",
    )
    mock_repo_instance.iter_records.assert_called_once_with(max_results=None)
    assert mock_repo_instance.delete.call_count == len(mock_records)
    mock_repo_instance.delete.assert_any_call("item1")
    mock_repo_instance.delete.assert_any_call("item2")


@pytest.mark.parametrize(
    "entity_type, expected_class",
    [
        (ClearableEntityTypes.organisation, Organisation),
        (ClearableEntityTypes.healthcare_service, HealthcareService),
        (ClearableEntityTypes.location, Location),
    ],
)
def test_get_entity_cls(
    entity_type: ClearableEntityTypes,
    expected_class: type,
) -> None:
    result = _get_entity_cls(entity_type)
    assert result == expected_class


def test_get_entity_cls_invalid_type() -> None:
    with pytest.raises(ValueError, match="Unsupported entity type: invalid_type"):
        _get_entity_cls("invalid_type")
