from typing import Generic, TypeVar

from ftrs_data_layer.domain.legacy.db_models import (
    Disposition,
    LegacyDoSModel,
    OpeningTimeDay,
    ServiceType,
    SymptomDiscriminator,
    SymptomGroup,
)
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, joinedload

DoSModelType = TypeVar("DoSModelType", bound=LegacyDoSModel)


class SQLAlchemyKVCache(Generic[DoSModelType]):
    """
    A simple key-value cache for storing and retrieving data.
    """

    def __init__(
        self,
        engine: Engine,
        model: type[DoSModelType],
        prejoin: bool = False,
    ) -> None:
        self.cache: dict[int, DoSModelType] = {}
        self.engine = engine
        self.model = model
        self.prejoin = prejoin

    def get(self, key: int) -> DoSModelType:
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

    def _retrieve_item(self, key: int) -> DoSModelType | None:
        """
        Retrieve an item from the database using the provided key.
        """
        with Session(self.engine) as session:
            stmt = select(self.model).where(self.model.id == key)
            if self.prejoin:
                stmt = stmt.options(joinedload("*"))

            return session.execute(stmt).unique().scalar_one_or_none()


class DoSMetadataCache:
    """
    Metadata class to hold common DoS metadata
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.symptom_groups = SQLAlchemyKVCache(engine, SymptomGroup)
        self.symptom_discriminators = SQLAlchemyKVCache(
            engine, SymptomDiscriminator, prejoin=True
        )
        self.dispositions = SQLAlchemyKVCache(engine, Disposition)
        self.opening_time_days = SQLAlchemyKVCache(engine, OpeningTimeDay)
        self.service_types = SQLAlchemyKVCache(engine, ServiceType)
