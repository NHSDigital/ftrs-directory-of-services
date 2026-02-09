from ftrs_data_layer.domain.legacy.clinical_codes import (
    Disposition,
    SymptomDiscriminator,
    SymptomDiscriminatorSynonym,
    SymptomGroup,
    SymptomGroupSymptomDiscriminator,
)
from ftrs_data_layer.domain.legacy.base import LegacyDoSModel


class TestSymptomGroup:
    """Tests for SymptomGroup legacy model."""

    def test_symptom_group_table_name(self) -> None:
        """Test that SymptomGroup has correct table name."""
        assert SymptomGroup.__tablename__ == "symptomgroups"

    def test_symptom_group_inherits_legacy_dos_model(self) -> None:
        """Test that SymptomGroup inherits from LegacyDoSModel."""
        assert issubclass(SymptomGroup, LegacyDoSModel)

    def test_create_symptom_group(self) -> None:
        """Test creating SymptomGroup instance."""
        sg = SymptomGroup(id=1000, name="Chest Pain", zcodeexists=True)

        assert sg.id == 1000
        assert sg.name == "Chest Pain"
        assert sg.zcodeexists is True

    def test_symptom_group_nullable_zcodeexists(self) -> None:
        """Test that zcodeexists can be None."""
        sg = SymptomGroup(id=1001, name="Headache", zcodeexists=None)

        assert sg.zcodeexists is None

    def test_symptom_group_has_required_id(self) -> None:
        """Test that SymptomGroup has id as primary key."""
        sg = SymptomGroup(id=1002, name="Test")
        assert sg.id == 1002


class TestSymptomDiscriminator:
    """Tests for SymptomDiscriminator legacy model."""

    def test_symptom_discriminator_table_name(self) -> None:
        """Test that SymptomDiscriminator has correct table name."""
        assert SymptomDiscriminator.__tablename__ == "symptomdiscriminators"

    def test_symptom_discriminator_inherits_legacy_dos_model(self) -> None:
        """Test that SymptomDiscriminator inherits from LegacyDoSModel."""
        assert issubclass(SymptomDiscriminator, LegacyDoSModel)

    def test_create_symptom_discriminator(self) -> None:
        """Test creating SymptomDiscriminator instance."""
        sd = SymptomDiscriminator(id=4003, description="Severe pain")

        assert sd.id == 4003
        assert sd.description == "Severe pain"

    def test_symptom_discriminator_nullable_description(self) -> None:
        """Test that description can be None."""
        sd = SymptomDiscriminator(id=4004, description=None)

        assert sd.description is None

    def test_symptom_discriminator_has_synonyms_relationship(self) -> None:
        """Test that SymptomDiscriminator has synonyms relationship defined."""
        sd = SymptomDiscriminator(id=4005, description="Test")

        # Should have synonyms attribute (relationship)
        assert hasattr(sd, "synonyms")


class TestSymptomDiscriminatorSynonym:
    """Tests for SymptomDiscriminatorSynonym legacy model."""

    def test_synonym_table_name(self) -> None:
        """Test that SymptomDiscriminatorSynonym has correct table name."""
        assert (
            SymptomDiscriminatorSynonym.__tablename__ == "symptomdiscriminatorsynonyms"
        )

    def test_synonym_inherits_legacy_dos_model(self) -> None:
        """Test that SymptomDiscriminatorSynonym inherits from LegacyDoSModel."""
        assert issubclass(SymptomDiscriminatorSynonym, LegacyDoSModel)

    def test_create_synonym(self) -> None:
        """Test creating SymptomDiscriminatorSynonym instance."""
        synonym = SymptomDiscriminatorSynonym(
            id=1, name="intense pain", symptomdiscriminatorid=4003
        )

        assert synonym.id == 1
        assert synonym.name == "intense pain"
        assert synonym.symptomdiscriminatorid == 4003

    def test_synonym_nullable_name(self) -> None:
        """Test that name can be None."""
        synonym = SymptomDiscriminatorSynonym(
            id=2, name=None, symptomdiscriminatorid=4003
        )

        assert synonym.name is None


class TestSymptomGroupSymptomDiscriminator:
    """Tests for SymptomGroupSymptomDiscriminator legacy model."""

    def test_sgsd_table_name(self) -> None:
        """Test that SymptomGroupSymptomDiscriminator has correct table name."""
        assert (
            SymptomGroupSymptomDiscriminator.__tablename__
            == "symptomgroupsymptomdiscriminators"
        )

    def test_sgsd_inherits_legacy_dos_model(self) -> None:
        """Test that SymptomGroupSymptomDiscriminator inherits from LegacyDoSModel."""
        assert issubclass(SymptomGroupSymptomDiscriminator, LegacyDoSModel)

    def test_create_sgsd(self) -> None:
        """Test creating SymptomGroupSymptomDiscriminator instance."""
        sgsd = SymptomGroupSymptomDiscriminator(
            id=1, symptomgroupid=1000, symptomdiscriminatorid=4003
        )

        assert sgsd.id == 1
        assert sgsd.symptomgroupid == 1000
        assert sgsd.symptomdiscriminatorid == 4003

    def test_sgsd_has_relationships(self) -> None:
        """Test that SymptomGroupSymptomDiscriminator has relationship attributes."""
        sgsd = SymptomGroupSymptomDiscriminator(
            id=2, symptomgroupid=1001, symptomdiscriminatorid=4004
        )

        assert hasattr(sgsd, "symptomgroup")
        assert hasattr(sgsd, "symptomdiscriminator")


class TestDisposition:
    """Tests for Disposition legacy model."""

    def test_disposition_table_name(self) -> None:
        """Test that Disposition has correct table name."""
        assert Disposition.__tablename__ == "dispositions"

    def test_disposition_inherits_legacy_dos_model(self) -> None:
        """Test that Disposition inherits from LegacyDoSModel."""
        assert issubclass(Disposition, LegacyDoSModel)

    def test_create_disposition(self) -> None:
        """Test creating Disposition instance."""
        disposition = Disposition(
            id=114,
            name="Attend ED within 4 hours",
            dxcode="DX114",
            dispositiontime=240,
        )

        assert disposition.id == 114
        assert disposition.name == "Attend ED within 4 hours"
        assert disposition.dxcode == "DX114"
        assert disposition.dispositiontime == 240

    def test_disposition_nullable_fields(self) -> None:
        """Test that dxcode and dispositiontime can be None."""
        disposition = Disposition(
            id=115,
            name="Test disposition",
            dxcode=None,
            dispositiontime=None,
        )

        assert disposition.dxcode is None
        assert disposition.dispositiontime is None
