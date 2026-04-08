from pathlib import Path

from devis_batiment.storage import Database


def test_database_initialize_creates_expected_tables(tmp_path: Path):
    database = Database(tmp_path / "test.db")

    database.initialize()

    table_names = database.list_tables()
    assert table_names == [
        "adjustment_rules",
        "breakdown_rules",
        "pricing_profiles",
        "quotes",
    ]
