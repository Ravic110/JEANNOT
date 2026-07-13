from __future__ import annotations

from dataclasses import dataclass

from devis_batiment.models import MaterialLine, QuoteEstimate, QuoteInput

DEFAULT_MATERIAL_UNITS: dict[str, str] = {
    "Ciment": "sacs 50kg",
    "Sable": "m³",
    "Gravier": "m³",
    "Fer": "kg",
    "Main d'œuvre": "jour",
}

DEFAULT_MATERIAL_QUANTITIES: dict[str, object] = {
    "Ciment": lambda volume: volume * 7.0,
    "Sable": lambda volume: volume * 0.5,
    "Gravier": lambda volume: volume * 0.7,
    "Fer": lambda volume: volume * 80.0,
    "Main d'œuvre": lambda quote_input, volume: max(1.0, quote_input.surface_m2 / 20.0),
}

DEFAULT_MATERIAL_PRICES: dict[str, float] = {
    "Ciment": 45_000.0,
    "Sable": 180_000.0,
    "Gravier": 190_000.0,
    "Fer": 4_000.0,
    "Main d'œuvre": 220_000.0,
}

PROJECT_VOLUME_FACTORS: dict[str, float] = {
    "Maison": 0.12,
    "Route": 0.18,
    "Autre": 0.10,
}


class MissingMaterialPriceError(ValueError):
    pass


class BtpQuoteCalculator:
    def __init__(
        self,
        material_prices: dict[str, dict[str, object]],
        adjustment_rules: dict[tuple[str, str], float] | None = None,
        breakdown_rules: dict[str, float] | None = None,
        safety_margin_pct: float = 0.0,
    ) -> None:
        self.material_prices = material_prices
        self.adjustment_rules = adjustment_rules or {}
        self.breakdown_rules = breakdown_rules or {}
        self.safety_margin_pct = safety_margin_pct

    def calculate(self, quote_input: QuoteInput) -> QuoteEstimate:
        volume_m3 = self._calculate_volume(quote_input)
        material_lines = self._build_material_lines(quote_input, volume_m3)

        total_amount = sum(line.line_total for line in material_lines)

        adj_map: dict[str, str | None] = {
            "location": quote_input.location,
            "structure_type": quote_input.structure_type,
            "roof_type": quote_input.roof_type,
            "complexity": quote_input.complexity,
            "floors": str(quote_input.floors) if quote_input.floors is not None and quote_input.floors <= 4 else "5+",
        }

        ordered_multipliers: dict[str, float] = {}
        for category, value in adj_map.items():
            key = (category, str(value)) if value is not None else (category, "")
            multiplier = self.adjustment_rules.get(key, 1.0)
            ordered_multipliers[category] = multiplier
            total_amount *= multiplier

        margin_factor = 1.0 + self.safety_margin_pct / 100.0
        total_amount = round(total_amount * margin_factor)
        ordered_multipliers["Marge de sécurité"] = margin_factor

        breakdown = {
            lot_name: round(total_amount * percentage)
            for lot_name, percentage in self.breakdown_rules.items()
        }
        if not breakdown:
            breakdown = {"Matériaux et main d'œuvre": total_amount}

        return QuoteEstimate(
            total_amount=total_amount,
            applied_multipliers=ordered_multipliers,
            breakdown=breakdown,
            materials=material_lines,
            volume_m3=volume_m3,
        )

    def _calculate_volume(self, quote_input: QuoteInput) -> float:
        project_type = quote_input.project_type
        if project_type == "Mur":
            return max(0.0, quote_input.length_m * quote_input.height_m * quote_input.thickness_m)

        if project_type == "Dalle béton":
            return max(0.0, quote_input.length_m * quote_input.width_m * quote_input.thickness_m)

        if project_type == "Route":
            thickness = quote_input.thickness_m or 0.15
            return max(0.0, quote_input.surface_m2 * thickness)

        factor = PROJECT_VOLUME_FACTORS.get(project_type, PROJECT_VOLUME_FACTORS["Autre"])
        return max(0.0, quote_input.surface_m2 * factor)

    def _build_material_lines(
        self, quote_input: QuoteInput, volume_m3: float
    ) -> list[MaterialLine]:
        base_quantities = {
            "Ciment": float(DEFAULT_MATERIAL_QUANTITIES["Ciment"](volume_m3)),
            "Sable": float(DEFAULT_MATERIAL_QUANTITIES["Sable"](volume_m3)),
            "Gravier": float(DEFAULT_MATERIAL_QUANTITIES["Gravier"](volume_m3)),
            "Fer": float(DEFAULT_MATERIAL_QUANTITIES["Fer"](volume_m3)),
            "Main d'œuvre": float(DEFAULT_MATERIAL_QUANTITIES["Main d'œuvre"](quote_input, volume_m3)),
        }

        lines: list[MaterialLine] = []
        for name, quantity in base_quantities.items():
            price = self._get_material_price(name)
            line_total = round(quantity * price)
            lines.append(
                MaterialLine(
                    name=name,
                    unit=DEFAULT_MATERIAL_UNITS[name],
                    quantity=round(quantity, 2),
                    unit_price=price,
                    line_total=line_total,
                )
            )
        return lines

    def _get_material_price(self, name: str) -> float:
        row = self.material_prices.get(name)
        if row is not None and row.get("unit_price") is not None:
            return float(row["unit_price"])
        if name in DEFAULT_MATERIAL_PRICES:
            return DEFAULT_MATERIAL_PRICES[name]
        raise MissingMaterialPriceError(f"Prix du matériau manquant : {name}")
