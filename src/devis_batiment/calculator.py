from __future__ import annotations

from devis_batiment.models import QuoteEstimate, QuoteInput


class EstimateCalculator:
    def __init__(
        self,
        pricing_profiles: dict[tuple[str, str], float],
        adjustment_rules: dict[tuple[str, str], float],
        breakdown_rules: dict[str, float],
    ) -> None:
        self.pricing_profiles = pricing_profiles
        self.adjustment_rules = adjustment_rules
        self.breakdown_rules = breakdown_rules

    def calculate(self, quote_input: QuoteInput) -> QuoteEstimate:
        base_price = self.pricing_profiles[(quote_input.building_type, quote_input.finish_level)]
        multipliers = {
            "location": self.adjustment_rules[("location", quote_input.location)],
            "structure_type": self.adjustment_rules[("structure_type", quote_input.structure_type)],
            "roof_type": self.adjustment_rules[("roof_type", quote_input.roof_type)],
            "complexity": self.adjustment_rules[("complexity", quote_input.complexity)],
            "floors": self.adjustment_rules[("floors", str(quote_input.floors))],
        }
        total_amount = quote_input.surface_m2 * base_price
        for multiplier in multipliers.values():
            total_amount *= multiplier
        breakdown = {
            lot_name: total_amount * percentage
            for lot_name, percentage in self.breakdown_rules.items()
        }
        return QuoteEstimate(
            total_amount=total_amount,
            applied_multipliers=multipliers,
            breakdown=breakdown,
        )
