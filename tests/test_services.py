from pathlib import Path

from devis_batiment.models import QuoteEstimate, QuoteInput
from devis_batiment.services import AdminService, QuoteService
from devis_batiment.storage import Database


def test_quote_service_saves_and_lists_quotes(tmp_path: Path):
    database = Database(tmp_path / "quotes.db")
    database.initialize()

    service = QuoteService(database)
    quote_input = QuoteInput(
        client_name="Mme Ranaivo",
        client_contact="0321111111",
        building_type="Villa",
        location="Toamasina",
        surface_m2=95,
        floors=1,
        structure_type="Beton arme",
        roof_type="Bac acier",
        room_count=4,
        finish_level="Economique",
        complexity="Simple",
    )
    estimate = QuoteEstimate(
        total_amount=56_000_000.0,
        applied_multipliers={"location": 1.02},
        breakdown={"Fondations": 11_200_000.0},
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
    service.save_pricing_profile("Villa", "Standard", 800_000)
    service.save_adjustment_rule("roof_type", "Tuile", 1.08)
    service.save_breakdown_rule("Fondations", 0.20)

    assert service.list_pricing_profiles() == [
        {"building_type": "Villa", "finish_level": "Standard", "base_price_per_m2": 800_000.0}
    ]
    assert service.list_adjustment_rules()[0]["rule_key"] == "Tuile"
    assert service.list_breakdown_rules()[0]["lot_name"] == "Fondations"
