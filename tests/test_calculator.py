from devis_batiment.models import QuoteInput
from devis_batiment.services.calcul_btp import BtpQuoteCalculator


def test_btp_calculator_computes_quote_from_dimensions():
    quote_input = QuoteInput(
        client_name="Client Demo",
        client_contact="0340000000",
        project_name="Maison 3 pièces",
        project_type="Maison",
        location="Antananarivo",
        surface_m2=120,
        length_m=0.0,
        width_m=0.0,
        height_m=0.0,
        thickness_m=0.0,
        floors=1,
        structure_type="Béton armé",
        roof_type="Tuile",
        room_count=5,
        finish_level="Standard",
        complexity="Moyenne",
        notes="Projet test",
    )

    calculator = BtpQuoteCalculator(
        material_prices={
            "Ciment": {"unit": "sacs 50kg", "unit_price": 45_000.0},
            "Sable": {"unit": "m³", "unit_price": 180_000.0},
            "Gravier": {"unit": "m³", "unit_price": 190_000.0},
            "Fer": {"unit": "kg", "unit_price": 4_000.0},
            "Main d'œuvre": {"unit": "jour", "unit_price": 220_000.0},
        },
        adjustment_rules={},
        breakdown_rules={
            "Matériaux et main d'œuvre": 1.0,
        },
        safety_margin_pct=0.0,
    )

    estimate = calculator.calculate(quote_input)

    assert estimate.total_amount > 0
    assert len(estimate.materials) >= 5
    assert estimate.volume_m3 > 0
    assert "Marge de sécurité" in estimate.applied_multipliers
