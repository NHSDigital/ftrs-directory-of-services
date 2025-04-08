from abc import ABC, abstractmethod
from typing import Generator, Generic, Type, TypeVar
from uuid import UUID

from ftrs_common.logger import Logger
from ftrs_data_layer.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(ABC, Generic[ModelType]):
    """
    Base repository class for CRUD operations.
    """

    model_cls: Type[ModelType]

    def __init__(
        self, model_cls: Type[ModelType], logger: Logger | None = None
    ) -> None:
        self.logger = logger or Logger.get(service="ftrs_data_layer")
        self.model_cls = model_cls
        if not issubclass(model_cls, BaseModel):
            error_msg = (
                f"Expected model_cls to be a subclass of BaseModel, got {model_cls}"
            )
            raise TypeError(error_msg)

    @abstractmethod
    def create(self, obj: ModelType) -> ModelType:
        """
        Create a new object in the database.
        """
        raise NotImplementedError("Create method not implemented.")

    @abstractmethod
    def get(self, id: str | UUID) -> ModelType:
        """
        Read an object from the database by ID.
        """
        raise NotImplementedError("Read method not implemented.")

    @abstractmethod
    def update(self, id: str | UUID, obj: ModelType) -> ModelType:
        """
        Update an existing object in the database.
        """
        raise NotImplementedError("Update method not implemented.")

    @abstractmethod
    def delete(self, id: str | UUID) -> None:
        """
        Delete an object from the database by ID.
        """
        raise NotImplementedError("Delete method not implemented.")

    @abstractmethod
    def iter_records(
        self, max_results: int | None = 100
    ) -> Generator[ModelType, None, None]:
        """
        Iterates over records in the table.
        """
        raise NotImplementedError("Iterate records method not implemented.")
