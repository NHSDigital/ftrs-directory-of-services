import pytest
from dynamodb.utils import get_table_name


def test_get_table_name_no_workspace() -> None:
    result = get_table_name(entity_type="healthcare", env="dev")
    assert result == "ftrs-dos-dev-database-healthcare"


def test_get_table_name_with_workspace() -> None:
    result = get_table_name(entity_type="location", env="local", workspace="test")
    assert result == "ftrs-dos-local-database-location-test"


def test_get_table_name_empty_entity_type() -> None:
    with pytest.raises(ValueError):
        get_table_name(entity_type="", env="dev")
