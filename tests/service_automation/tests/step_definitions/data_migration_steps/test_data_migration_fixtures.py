from sqlalchemy import text
from sqlmodel import Session

from utilities.common.legacy_dos_rds_tables import LEGACY_DOS_TABLES


class TestDoSDbWithMigrationFixture:
    """Test suite for the dos_db_with_migration fixture."""

    def test_migration_fixture_creates_schema(self, dos_db_with_migration: Session):
        """Test that the migration fixture creates the pathwaysdos schema."""
        result = dos_db_with_migration.exec(
            text(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'pathwaysdos'"
            )
        )
        schemas = result.fetchall()
        assert len(schemas) == 1
        assert schemas[0][0] == "pathwaysdos"

    def test_migration_fixture_creates_tables(self, dos_db_with_migration: Session):
        """Test that the migration fixture creates all required tables."""

        # Query for all tables in the pathwaysdos schema
        result = dos_db_with_migration.exec(
                    text("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'pathwaysdos'
                        AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """)
        )
        actual_tables = [row[0] for row in result.fetchall()]

        # Check that all expected tables exist
        for table in LEGACY_DOS_TABLES:
            assert table in actual_tables, (
                f"Table {table} not found in migrated database"
            )

    def test_servicetypes_table_has_data(self, dos_db_with_migration: Session):
        """Test that the servicetypes table contains migrated data."""
        result = dos_db_with_migration.exec(
            text("SELECT COUNT(*) FROM pathwaysdos.servicetypes")
        )
        count = result.fetchone()[0]
        assert count > 0, "servicetypes table should contain migrated data"

    def test_services_table_has_data(self, dos_db_with_migration: Session):
        """Test that the services table contains migrated data."""
        result = dos_db_with_migration.exec(
            text("SELECT COUNT(*) FROM pathwaysdos.services")
        )
        count = result.fetchone()[0]
        assert count > 0, "services table should contain migrated data"

    def test_migration_fixture_isolation(self, dos_db_with_migration: Session):
        dos_db_with_migration.exec(
            text(
                "INSERT INTO pathwaysdos.organisationtypes (id, name) VALUES (999, 'Test Organisation Type')"
            )
        )
        dos_db_with_migration.commit()

        # Verify the record exists
        result = dos_db_with_migration.exec(
            text("SELECT name FROM pathwaysdos.organisationtypes WHERE id = 999")
        )
        test_org = result.fetchone()
        assert test_org is not None
        assert test_org[0] == "Test Organisation Type"
