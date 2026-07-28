from pathlib import Path

from devis_batiment.models import MaterialLine, QuoteEstimate, QuoteInput
from devis_batiment.services import (
    AdminService,
    ClientService,
    QuoteWorkflow,
    TemplateService,
)
from devis_batiment.storage import Database


def _seed_materials(database: Database) -> None:
    admin = AdminService(database)
    admin.save_material("Ciment", "sacs 50kg", 45_000)
    admin.save_material("Sable", "m³", 180_000)
    admin.save_material("Gravier", "m³", 190_000)
    admin.save_material("Fer", "kg", 4_000)
    admin.save_material("Main d'œuvre", "jour", 220_000)
    admin.save_breakdown_rule("Matériaux", 0.8)
    admin.save_breakdown_rule("Main d'œuvre", 0.2)


def _make_input(client_name: str = "M. Rakoto", contact: str = "0330000000") -> QuoteInput:
    return QuoteInput(
        client_name=client_name,
        client_contact=contact,
        project_name="Villa",
        project_type="Maison",
        location="Antananarivo",
        surface_m2=100.0,
        length_m=0.0,
        width_m=0.0,
        height_m=0.0,
        thickness_m=0.0,
        floors=1,
        structure_type="Béton armé",
        roof_type="Tôle",
        room_count=4,
        finish_level="Standard",
        complexity="Simple",
    )


def _make_estimate(total: float = 10_000_000.0) -> QuoteEstimate:
    return QuoteEstimate(
        total_amount=total,
        applied_multipliers={"Marge de sécurité": 1.0},
        breakdown={"Matériaux": total},
        materials=[MaterialLine("Ciment", "sacs", 100, 45_000, 4_500_000)],
        volume_m3=10.0,
    )


# --- Lot B : statut des devis ---


def test_new_quote_defaults_to_brouillon(tmp_path: Path):
    database = Database(tmp_path / "status.db")
    database.initialize()

    quote_id = database.insert_quote(_make_input(), _make_estimate())

    rows = database.fetch_quotes()
    assert rows[0]["id"] == quote_id
    assert rows[0]["status"] == "Brouillon"


def test_update_quote_status_changes_status(tmp_path: Path):
    database = Database(tmp_path / "status.db")
    database.initialize()
    quote_id = database.insert_quote(_make_input(), _make_estimate())

    database.update_quote_status(quote_id, "Accepté")

    assert database.fetch_quotes()[0]["status"] == "Accepté"


def test_count_quotes_by_status(tmp_path: Path):
    database = Database(tmp_path / "status.db")
    database.initialize()
    a = database.insert_quote(_make_input(), _make_estimate())
    b = database.insert_quote(_make_input(), _make_estimate())
    database.insert_quote(_make_input(), _make_estimate())
    database.update_quote_status(a, "Accepté")
    database.update_quote_status(b, "Envoyé")

    counts = database.count_quotes_by_status()

    assert counts["Accepté"] == 1
    assert counts["Envoyé"] == 1
    assert counts["Brouillon"] == 1


def test_sum_amount_by_status(tmp_path: Path):
    database = Database(tmp_path / "status.db")
    database.initialize()
    a = database.insert_quote(_make_input(), _make_estimate(20_000_000.0))
    database.insert_quote(_make_input(), _make_estimate(5_000_000.0))
    database.update_quote_status(a, "Accepté")

    assert database.sum_amount_by_status("Accepté") == 20_000_000.0
    assert database.sum_amount_by_status("Brouillon") == 5_000_000.0


def test_legacy_quotes_table_is_migrated(tmp_path: Path):
    """Une base sans les colonnes status/client_id doit rester lisible."""
    import sqlite3

    db_path = tmp_path / "legacy.db"
    legacy = sqlite3.connect(db_path)
    legacy.executescript(
        """
        CREATE TABLE quotes (
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            client_name TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            total_amount REAL NOT NULL
        );
        INSERT INTO quotes(created_at, client_name, payload_json, total_amount)
        VALUES ('2026-01-01', 'Ancien client', '{}', 1000000.0);
        """
    )
    legacy.commit()
    legacy.close()

    database = Database(db_path)
    database.initialize()

    rows = database.fetch_quotes()
    assert rows[0]["client_name"] == "Ancien client"
    assert rows[0]["status"] == "Brouillon"


# --- Lot A : fiches clients enrichies + lien devis↔clients ---


def test_save_and_get_enriched_client(tmp_path: Path):
    database = Database(tmp_path / "clients.db")
    database.initialize()

    client_id = database.insert_client(
        "SARL Betonline",
        contact="0340000000",
        client_type="Entreprise",
        email="contact@betonline.mg",
        phone="0340000000",
        address="Lot II Antananarivo",
        site_address="Chantier Ivandry",
        notes="Client fidèle",
    )

    client = database.get_client(client_id)
    assert client["name"] == "SARL Betonline"
    assert client["client_type"] == "Entreprise"
    assert client["email"] == "contact@betonline.mg"
    assert client["address"] == "Lot II Antananarivo"
    assert client["site_address"] == "Chantier Ivandry"
    assert client["notes"] == "Client fidèle"


def test_list_clients_filters_by_type_and_search(tmp_path: Path):
    database = Database(tmp_path / "clients.db")
    database.initialize()
    database.insert_client("M. Rakoto", client_type="Particulier")
    database.insert_client("SARL Betonline", client_type="Entreprise")
    database.insert_client("Mme Rasoa", client_type="Particulier")

    entreprises = database.fetch_clients(client_type="Entreprise")
    assert [c["name"] for c in entreprises] == ["SARL Betonline"]

    rako = database.fetch_clients(search="rako")
    assert [c["name"] for c in rako] == ["M. Rakoto"]


def test_service_ensure_client_preserves_enriched_fields(tmp_path: Path):
    database = Database(tmp_path / "clients.db")
    database.initialize()
    client_id = database.insert_client(
        "M. Rakoto",
        client_type="Entreprise",
        address="Lot II",
    )

    # Un ré-appel « léger » (nom + contact seulement) ne doit pas écraser
    # les champs enrichis existants.
    same_id = database.ensure_client("M. Rakoto", "0331234567")

    assert same_id == client_id
    client = database.get_client(client_id)
    assert client["client_type"] == "Entreprise"
    assert client["address"] == "Lot II"
    assert client["contact"] == "0331234567"


def test_create_quote_links_client(tmp_path: Path):
    database = Database(tmp_path / "clients.db")
    database.initialize()
    _seed_materials(database)

    workflow = QuoteWorkflow(database)
    quote_id, _ = workflow.create_quote(_make_input("Mme Ranaivo", "0321111111"))

    clients = database.fetch_clients()
    assert [c["name"] for c in clients] == ["Mme Ranaivo"]
    client_id = clients[0]["id"]

    linked = database.list_quotes_for_client(client_id)
    assert len(linked) == 1
    assert linked[0]["id"] == quote_id
    assert linked[0]["status"] == "Brouillon"


def test_client_service_lists_quotes_for_client(tmp_path: Path):
    database = Database(tmp_path / "clients.db")
    database.initialize()
    _seed_materials(database)
    workflow = QuoteWorkflow(database)
    workflow.create_quote(_make_input("M. Rakoto", "0332222222"))

    service = ClientService(database)
    client_id = service.list_clients()[0]["id"]
    assert len(service.list_quotes_for_client(client_id)) == 1


# --- Lot C : modèles de devis ---


def test_seed_creates_default_templates(tmp_path: Path):
    database = Database(tmp_path / "templates.db")
    database.initialize()

    AdminService(database).seed_defaults_if_empty()

    names = [t["name"] for t in database.fetch_templates()]
    assert "Maison standard" in names


def test_save_and_list_template_excludes_client(tmp_path: Path):
    database = Database(tmp_path / "templates.db")
    database.initialize()
    service = TemplateService(database)

    service.save_template("Mon modèle", _make_input("Client secret", "0330000000"))

    templates = {t["name"]: t["payload"] for t in service.list_templates()}
    assert "Mon modèle" in templates
    payload = templates["Mon modèle"]
    assert payload["project_type"] == "Maison"
    assert payload["surface_m2"] == 100.0
    # Aucune information client dans un modèle.
    assert "client_name" not in payload
    assert "client_contact" not in payload


def test_delete_template(tmp_path: Path):
    database = Database(tmp_path / "templates.db")
    database.initialize()
    service = TemplateService(database)
    service.save_template("Temporaire", _make_input())

    service.delete_template("Temporaire")

    assert [t["name"] for t in service.list_templates()] == []
