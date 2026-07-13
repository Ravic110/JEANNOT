from pathlib import Path

from devis_batiment.models import MaterialLine, QuoteEstimate, QuoteInput
from devis_batiment.services import AdminService, QuoteService, QuoteWorkflow
from devis_batiment.storage import Database


def test_quote_service_saves_and_lists_quotes(tmp_path: Path):
    database = Database(tmp_path / "quotes.db")
    database.initialize()

    service = QuoteService(database)
    quote_input = QuoteInput(
        client_name="Mme Ranaivo",
        client_contact="0321111111",
        project_name="Villa côté mer",
        project_type="Maison",
        location="Toamasina",
        surface_m2=95,
        length_m=0.0,
        width_m=0.0,
        height_m=0.0,
        thickness_m=0.0,
        floors=1,
        structure_type="Béton armé",
        roof_type="Tôle",
        room_count=4,
        finish_level="Économique",
        complexity="Simple",
    )
    estimate = QuoteEstimate(
        total_amount=56_000_000.0,
        applied_multipliers={"Marge de sécurité": 1.0},
        breakdown={"Matériaux": 56_000_000.0},
        materials=[
            MaterialLine("Ciment", "sacs", 100, 45_000, 4_500_000),
            MaterialLine("Sable", "m³", 50, 180_000, 9_000_000),
        ],
        volume_m3=11.4,
    )

    saved_id = service.save_quote(quote_input, estimate)
    rows = service.list_quotes()

    assert saved_id == 1
    assert rows[0]["client_name"] == "Mme Ranaivo"
    assert rows[0]["total_amount"] == 56_000_000.0


def test_admin_service_saves_and_reads_reference_rules(tmp_path: Path):
    database = Database(tmp_path / "admin.db")
    database.initialize()

    service = AdminService(database)
    service.save_adjustment_rule("roof_type", "Tuile", 1.08)
    service.save_breakdown_rule("Fondations", 0.20)
    service.save_material("Ciment", "sacs 50kg", 45_000)

    assert service.list_adjustment_rules()[0]["rule_key"] == "Tuile"
    assert service.list_breakdown_rules()[0]["lot_name"] == "Fondations"
    assert len(service.list_materials()) >= 1


def test_quote_workflow_uses_reference_data_and_persists_quote(tmp_path: Path):
    database = Database(tmp_path / "workflow.db")
    database.initialize()

    admin = AdminService(database)
    admin.save_material("Ciment", "sacs 50kg", 45_000)
    admin.save_material("Sable", "m³", 180_000)
    admin.save_material("Gravier", "m³", 190_000)
    admin.save_material("Fer", "kg", 4_000)
    admin.save_material("Main d'œuvre", "jour", 220_000)
    admin.save_breakdown_rule("Matériaux", 0.8)
    admin.save_breakdown_rule("Main d'œuvre", 0.2)

    workflow = QuoteWorkflow(database)
    saved_id, estimate = workflow.create_quote(
        QuoteInput(
            client_name="M. Rakoto",
            client_contact="0332222222",
            project_name="Dalle béton",
            project_type="Dalle béton",
            location="Antananarivo",
            surface_m2=100,
            length_m=10.0,
            width_m=10.0,
            height_m=0.15,
            thickness_m=0.15,
            floors=1,
            structure_type="Béton armé",
            roof_type="Terrasse béton",
            room_count=0,
            finish_level="Standard",
            complexity="Simple",
        )
    )

    assert saved_id == 1
    assert estimate.total_amount > 0
    assert len(estimate.materials) > 0


def test_quote_service_can_search_and_duplicate_quotes(tmp_path: Path):
    database = Database(tmp_path / "history.db")
    database.initialize()
    service = QuoteService(database)
    quote_input = QuoteInput(
        client_name="M. Rakoto",
        client_contact="0332222222",
        project_name="Mur de fondation",
        project_type="Mur",
        location="Antananarivo",
        surface_m2=120,
        length_m=50.0,
        width_m=0.0,
        height_m=2.4,
        thickness_m=0.3,
        floors=1,
        structure_type="Béton armé",
        roof_type="N/A",
        room_count=5,
        finish_level="Standard",
        complexity="Moyenne",
    )
    estimate = QuoteEstimate(
        total_amount=108_864_000.0,
        applied_multipliers={"Marge de sécurité": 1.0},
        breakdown={"Matériaux": 87_091_200.0, "Main d'œuvre": 21_772_800.0},
        materials=[
            MaterialLine("Ciment", "sacs", 840, 45_000, 37_800_000),
            MaterialLine("Sable", "m³", 420, 180_000, 75_600_000),
        ],
        volume_m3=36.0,
    )

    original_id = service.save_quote(quote_input, estimate)
    duplicated_id = service.duplicate_quote(original_id)
    results = service.search_quotes("Rakoto")

    assert duplicated_id == 2
    assert len(results) == 2
    assert results[0]["client_name"] == "M. Rakoto"


def test_quote_service_loads_persisted_quote(tmp_path: Path):
    database = Database(tmp_path / "load.db")
    database.initialize()
    service = QuoteService(database)
    quote_input = QuoteInput(
        client_name="Mme Ranaivo",
        client_contact="0321111111",
        project_name="Villa",
        project_type="Maison",
        location="Toamasina",
        surface_m2=95,
        length_m=0.0,
        width_m=0.0,
        height_m=0.0,
        thickness_m=0.0,
        floors=1,
        structure_type="Béton armé",
        roof_type="Tôle",
        room_count=4,
        finish_level="Économique",
        complexity="Simple",
    )
    estimate = QuoteEstimate(
        total_amount=56_000_000.0,
        applied_multipliers={"Marge de sécurité": 1.0},
        breakdown={"Matériaux": 56_000_000.0},
        materials=[MaterialLine("Ciment", "sacs", 100, 45_000, 4_500_000)],
        volume_m3=11.4,
    )
    saved_id = service.save_quote(quote_input, estimate)

    loaded_input, loaded_estimate = service.load_quote(saved_id)

    assert loaded_input == quote_input
    assert loaded_estimate.total_amount == 56_000_000.0
    assert loaded_estimate.materials[0].name == "Ciment"
    assert loaded_estimate.volume_m3 == 11.4
