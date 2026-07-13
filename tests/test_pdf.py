from pathlib import Path

from devis_batiment.models import MaterialLine, QuoteEstimate, QuoteInput
from devis_batiment.utils.pdf import export_quote_pdf


def test_export_quote_pdf_writes_non_empty_file(tmp_path: Path):
    quote_input = QuoteInput(
        client_name="Client Test", client_contact="0340000000",
        project_name="Maison", project_type="Maison", location="Antananarivo",
        surface_m2=100, length_m=0.0, width_m=0.0, height_m=0.0, thickness_m=0.0,
        floors=1, structure_type="Béton armé", roof_type="Tôle", room_count=3,
        finish_level="Standard", complexity="Simple",
    )
    estimate = QuoteEstimate(
        total_amount=12_000_000.0, applied_multipliers={"Marge de sécurité": 1.0},
        breakdown={"Matériaux": 12_000_000.0},
        materials=[MaterialLine("Ciment", "sacs 50kg", 10, 45_000, 450_000)],
        volume_m3=5.0,
    )
    company_info = {"company_name": "Jeannot Devis Bâtiment", "currency": "Ar"}
    output = tmp_path / "devis_1.pdf"

    result = export_quote_pdf(output, company_info, 1, quote_input, estimate)

    assert result == output
    assert output.exists()
    assert output.stat().st_size > 0
