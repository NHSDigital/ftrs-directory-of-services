import pytest

from ftrs_data_layer.models import BaseModel
from ftrs_data_layer.repository.base import BaseRepository


class ExampleModel(BaseModel):
    id: str
    name: str


class ExampleRepository(BaseRepository[ExampleModel]):
    def create(self, obj: ExampleModel) -> ExampleModel:
        return super().create(obj)

    def get(self, id: str) -> ExampleModel:
        return super().get(id)

    def update(self, id: str, obj: ExampleModel) -> ExampleModel:
        return super().update(id, obj)

    def delete(self, id: str) -> None:
        return super().delete(id)

    def iter_records(self, max_results: int | None = 100) -> list[ExampleModel]:
        return super().iter_records(max_results)


def test_repository_initialisation() -> None:
    """
    Test the initialisation of the repository with a mock logger.
    """
    repo = ExampleRepository(model_cls=ExampleModel)
    assert repo.model_cls == ExampleModel


def test_repository_initialisation_with_invalid_model_cls() -> None:
    """
    Test the initialisation of the repository with an invalid model class.
    """
    with pytest.raises(TypeError) as excinfo:
        ExampleRepository(model_cls=str)

    assert (
        excinfo.exconly()
        == "TypeError: Expected model_cls to be a subclass of BaseModel, got <class 'str'>"
    )


def test_repository_initialisation_without_logger() -> None:
    """
    Test the initialisation of the repository without a logger.
    """
    repo = ExampleRepository(model_cls=ExampleModel)

    assert repo.model_cls == ExampleModel


def test_create_method() -> None:
    """
    Test the create method of the repository.
    """
    repo = ExampleRepository(model_cls=ExampleModel)
    obj = ExampleModel(id="1", name="Test")

    with pytest.raises(NotImplementedError):
        repo.create(obj)


def test_get_method() -> None:
    """
    Test the get method of the repository.
    """
    repo = ExampleRepository(model_cls=ExampleModel)

    with pytest.raises(NotImplementedError):
        repo.get("1")


def test_update_method() -> None:
    """
    Test the update method of the repository.
    """
    repo = ExampleRepository(model_cls=ExampleModel)
    obj = ExampleModel(id="1", name="Test")

    with pytest.raises(NotImplementedError):
        repo.update("1", obj)


def test_delete_method() -> None:
    """
    Test the delete method of the repository.
    """
    repo = ExampleRepository(model_cls=ExampleModel)

    with pytest.raises(NotImplementedError):
        repo.delete("1")


def test_iter_records_method() -> None:
    """
    Test the iter_records method of the repository.
    """
    repo = ExampleRepository(model_cls=ExampleModel)

    with pytest.raises(NotImplementedError):
        repo.iter_records()
