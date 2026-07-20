from pathlib import Path

from devis_batiment.storage import Database


def test_database_initialize_creates_expected_tables(tmp_path: Path):
    database = Database(tmp_path / "test.db")

    database.initialize()

    table_names = database.list_tables()
    assert sorted(table_names) == sorted([
        "adjustment_rules",
        "breakdown_rules",
        "quotes",
        "quote_lines",
        "clients",
        "projects",
        "materials",
        "settings",
        "quote_templates",
    ])


def test_deleting_client_cascades_to_projects(tmp_path: Path):
    database = Database(tmp_path / "cascade.db")
    database.initialize()

    client_id = database.insert_client("M. Rakoto", "0331111111")
    database.insert_project(client_id, "Villa", "Maison", "Antananarivo", "")

    assert len(database.fetch_projects()) == 1

    database.delete_client(client_id)

    assert database.fetch_projects() == []
    assert database.count_projects() == 0
