from ftrs_data_layer.domain.legacy.base import LegacyDoSModel
from sqlmodel import MetaData


class TestLegacyDoSModel:
    """Tests for LegacyDoSModel base class."""

    def test_legacy_dos_model_has_metadata(self) -> None:
        """Test that LegacyDoSModel has metadata attribute."""
        assert hasattr(LegacyDoSModel, "metadata")

    def test_legacy_dos_model_metadata_is_metadata_instance(self) -> None:
        """Test that LegacyDoSModel metadata is a MetaData instance."""
        assert isinstance(LegacyDoSModel.metadata, MetaData)

    def test_legacy_dos_model_schema_is_pathwaysdos(self) -> None:
        """Test that LegacyDoSModel uses pathwaysdos schema."""
        assert LegacyDoSModel.metadata.schema == "pathwaysdos"

    def test_legacy_dos_model_can_be_subclassed(self) -> None:
        """Test that LegacyDoSModel can be used as a base class."""

        class TestModel(LegacyDoSModel, table=False):
            """Test subclass for validation."""

            id: int
            name: str

        # Should be able to create instance
        instance = TestModel(id=1, name="test")
        assert instance.id == 1
        assert instance.name == "test"

    def test_legacy_dos_model_subclass_inherits_schema(self) -> None:
        """Test that subclasses inherit the pathwaysdos schema."""

        class TestSubModel(LegacyDoSModel, table=False):
            """Test subclass to verify schema inheritance."""

            id: int

        # Subclass should have same metadata
        assert TestSubModel.metadata.schema == "pathwaysdos"
