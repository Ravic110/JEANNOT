from devis_batiment.calculator import EstimateCalculator
from devis_batiment.models import QuoteInput


def test_estimate_calculator_applies_base_price_adjustments_and_breakdown():
    quote_input = QuoteInput(
        client_name="Client Demo",
        client_contact="0340000000",
        building_type="Villa",
        location="Antananarivo",
        surface_m2=120,
        floors=1,
        structure_type="Beton arme",
        roof_type="Tuile",
        room_count=5,
        finish_level="Standard",
        complexity="Normal",
    )

    calculator = EstimateCalculator(
        pricing_profiles={("Villa", "Standard"): 800_000},
        adjustment_rules={
            ("location", "Antananarivo"): 1.0,
            ("structure_type", "Beton arme"): 1.05,
            ("roof_type", "Tuile"): 1.08,
            ("complexity", "Normal"): 1.0,
            ("floors", "1"): 1.0,
        },
        breakdown_rules={
            "Fondations": 0.20,
            "Structure": 0.30,
            "Toiture": 0.15,
            "Finitions": 0.25,
            "Divers": 0.10,
        },
    )

    estimate = calculator.calculate(quote_input)

    assert round(estimate.total_amount, 2) == 108_864_000.00
    assert estimate.breakdown["Structure"] == 32_659_200.0
