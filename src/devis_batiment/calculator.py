from __future__ import annotations

from devis_batiment.models import QuoteEstimate, QuoteInput


class MissingReferenceError(ValueError):
    """Levée quand une donnée de référence est absente de la base."""


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
        profile_key = (quote_input.building_type, quote_input.finish_level)
        if profile_key not in self.pricing_profiles:
            raise MissingReferenceError(
                f"Aucun prix de base pour le type « {quote_input.building_type} » "
                f"avec finition « {quote_input.finish_level} ». "
                "Vérifiez les profils de prix dans l'Administration."
            )

        base_price = self.pricing_profiles[profile_key]

        floors_key = str(quote_input.floors) if quote_input.floors <= 4 else "5+"
        adj_keys = {
            "location": ("location", quote_input.location),
            "structure_type": ("structure_type", quote_input.structure_type),
            "roof_type": ("roof_type", quote_input.roof_type),
            "complexity": ("complexity", quote_input.complexity),
            "floors": ("floors", floors_key),
        }

        multipliers: dict[str, float] = {}
        missing: list[str] = []
        for label, key in adj_keys.items():
            if key in self.adjustment_rules:
                multipliers[label] = self.adjustment_rules[key]
            else:
                missing.append(f"{key[0]}={key[1]}")

        if missing:
            raise MissingReferenceError(
                "Coefficients d'ajustement manquants : " + ", ".join(missing) + ". "
                "Vérifiez les règles d'ajustement dans l'Administration."
            )

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
