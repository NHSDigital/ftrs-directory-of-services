from typing import Generic, TypeVar

from ftrs_data_layer.domain.legacy import (
    Disposition,
    OpeningTimeDay,
    SymptomDiscriminator,
    SymptomGroup,
)
from sqlalchemy import Engine
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

T = TypeVar("T")


class SQLModelKVCache(Generic[T]):
    """
    A simple key-value cache for storing and retrieving data.
    """

    def __init__(self, engine: Engine, model: type[T]) -> None:
        self.cache: dict[int, T] = {}
        self.engine = engine
        self.model = model

    def get(self, key: int) -> T:
        """
        Retrieve an item from the cache or database.
        If the item is not found in the cache, it will be fetched from the database.
        """
        if cached_item := self.cache.get(key):
            return cached_item

        if item := self._retrieve_item(key):
            self.cache[key] = item
            return item

        raise KeyError(
            f"Item with key {key} and model {self.model.__name__} not found in cache or database"
        )

    def _retrieve_item(self, key: int) -> T | None:
        """
        Retrieve an item from the database using the provided key.
        """
        with Session(self.engine) as session:
            stmt = (
                select(self.model).where(self.model.id == key).options(joinedload("*"))
            )

            return session.exec(stmt).unique().first()


class DoSMetadataCache:
    """
    Metadata class to hold common DoS metadata
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.symptom_groups = SQLModelKVCache(engine, SymptomGroup)
        self.symptom_discriminators = SQLModelKVCache(engine, SymptomDiscriminator)
        self.dispositions = SQLModelKVCache(engine, Disposition)
        self.opening_time_days = SQLModelKVCache(engine, OpeningTimeDay)
