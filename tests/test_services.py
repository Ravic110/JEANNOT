from pathlib import Path

from devis_batiment.models import QuoteEstimate, QuoteInput
from devis_batiment.services import QuoteService
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
