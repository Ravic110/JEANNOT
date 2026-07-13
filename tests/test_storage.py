from pathlib import Path

from devis_batiment.storage import Database


def test_database_initialize_creates_expected_tables(tmp_path: Path):
    database = Database(tmp_path / "test.db")

    database.initialize()

    table_names = database.list_tables()
    assert sorted(table_names) == sorted([
        "adjustment_rules",
        "breakdown_rules",
        "pricing_profiles",
        "quotes",
        "quote_lines",
        "clients",
        "projects",
        "materials",
        "settings",
    ])
