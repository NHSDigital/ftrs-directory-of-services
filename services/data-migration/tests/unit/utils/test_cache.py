import pytest
from ftrs_data_layer.domain.legacy import (
    Disposition,
    OpeningTimeDay,
    ServiceType,
    SymptomDiscriminator,
    SymptomGroup,
)
from ftrs_data_layer.domain.legacy.base import LegacyDoSModel
from pytest_mock import MockerFixture
from sqlalchemy import Engine
from sqlalchemy.engine.mock import create_mock_engine
from sqlmodel import Field

from pipeline.utils.cache import DoSMetadataCache, SQLModelKVCache


class MockModel(LegacyDoSModel, table=True):
    id: int = Field(primary_key=True)
    name: str


def test_sqlmodel_cache_init(mocker: MockerFixture) -> None:
    """
    Test that SQLModelKVCache initializes correctly with an engine and model.
    """
    engine = mocker.MagicMock(spec=Engine)

    cache = SQLModelKVCache(engine, MockModel)

    assert cache.engine == engine
    assert cache.model == MockModel
    assert isinstance(cache.cache, dict)


def test_sqlmodel_cache_get(mocker: MockerFixture) -> None:
    """
    Test that SQLModelKVCache.get retrieves an item from the cache or database.
    """
    engine = mocker.MagicMock(spec=Engine)
    cache = SQLModelKVCache(engine, MockModel)

    mock_item = MockModel(id=1, name="Test Item")
    cache._retrieve_item = mocker.MagicMock(return_value=mock_item)

    assert cache.cache == {}

    result = cache.get(1)
    assert result == mock_item

    assert cache._retrieve_item.call_count == 1
    cache._retrieve_item.assert_called_once_with(1)

    assert cache.cache == {1: mock_item}

    result = cache.get(1)
    assert result == mock_item

    assert cache._retrieve_item.call_count == 1  # Should not call again


def test_sqlmodel_cache_get_key_error(mocker: MockerFixture) -> None:
    """
    Test that SQLModelKVCache.get raises KeyError if the item is not found.
    """
    engine = mocker.MagicMock(spec=Engine)
    cache = SQLModelKVCache(engine, MockModel)

    cache._retrieve_item = mocker.MagicMock(return_value=None)

    with pytest.raises(
        KeyError,
        match="Item with key 1 and model MockModel not found in cache or database",
    ):
        cache.get(1)

    assert cache._retrieve_item.call_count == 1
    cache._retrieve_item.assert_called_once_with(1)


def test_sqlmodel_cache_retrieve_item(mocker: MockerFixture) -> None:
    """
    Test that SQLModelKVCache._retrieve_item retrieves an item from the database.
    """
    executor = mocker.MagicMock()
    engine = create_mock_engine(
        url="postgresql:///postgres:postgres@localhost:5432/postgres",
        executor=executor,
    )
    engine.begin = mocker.MagicMock()
    engine.close = mocker.MagicMock()
    engine.in_transaction = mocker.MagicMock(return_value=False)

    cache = SQLModelKVCache(engine, MockModel)
    cache._retrieve_item(1)

    executor.assert_called_once()
    statement = executor.mock_calls[0][1][0]

    compiled_statement = statement.compile(compile_kwargs={"literal_binds": True})
    assert str(compiled_statement) == (
        "SELECT pathwaysdos.mockmodel.id, pathwaysdos.mockmodel.name \n"
        "FROM pathwaysdos.mockmodel \n"
        "WHERE pathwaysdos.mockmodel.id = 1"
    )


def test_sqlmodel_cache_retrieve_item_prejoin(mocker: MockerFixture) -> None:
    """
    Test that SQLModelKVCache._retrieve_item retrieves an item from the database with a prejoin.
    """
    executor = mocker.MagicMock()
    engine = create_mock_engine(
        url="postgresql:///postgres:postgres@localhost:5432/postgres",
        executor=executor,
    )
    engine.begin = mocker.MagicMock()
    engine.close = mocker.MagicMock()
    engine.in_transaction = mocker.MagicMock(return_value=False)

    cache = SQLModelKVCache(engine, SymptomDiscriminator, prejoin=True)
    cache._retrieve_item(1)

    executor.assert_called_once()
    statement = executor.mock_calls[0][1][0]

    compiled_statement = statement.compile(compile_kwargs={"literal_binds": True})
    assert str(compiled_statement) == (
        "SELECT pathwaysdos.symptomdiscriminators.id, pathwaysdos.symptomdiscriminators.description, symptomdiscriminatorsynonyms_1.id AS id_1, symptomdiscriminatorsynonyms_1.name, symptomdiscriminatorsynonyms_1.symptomdiscriminatorid \n"
        "FROM pathwaysdos.symptomdiscriminators "
        "LEFT OUTER JOIN pathwaysdos.symptomdiscriminatorsynonyms AS symptomdiscriminatorsynonyms_1 ON pathwaysdos.symptomdiscriminators.id = symptomdiscriminatorsynonyms_1.symptomdiscriminatorid \n"
        "WHERE pathwaysdos.symptomdiscriminators.id = 1"
    )


def test_dos_metadata_cache_init(mocker: MockerFixture) -> None:
    """
    Test that DoSMetadataCache initializes correctly with an engine.
    """
    engine = mocker.MagicMock(spec=Engine)

    cache = DoSMetadataCache(engine)

    assert cache.engine == engine
    assert isinstance(cache.symptom_groups, SQLModelKVCache)
    assert isinstance(cache.symptom_discriminators, SQLModelKVCache)
    assert isinstance(cache.dispositions, SQLModelKVCache)
    assert isinstance(cache.opening_time_days, SQLModelKVCache)
    assert isinstance(cache.service_types, SQLModelKVCache)

    assert cache.symptom_groups.model == SymptomGroup
    assert cache.symptom_discriminators.model == SymptomDiscriminator
    assert cache.dispositions.model == Disposition
    assert cache.opening_time_days.model == OpeningTimeDay
    assert cache.service_types.model == ServiceType

    assert cache.symptom_groups.prejoin is False
    assert cache.symptom_discriminators.prejoin is True  # Needed for synonyms
    assert cache.dispositions.prejoin is False
    assert cache.opening_time_days.prejoin is False
    assert cache.service_types.prejoin is False
