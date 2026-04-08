from __future__ import annotations

from devis_batiment.models import QuoteEstimate, QuoteInput
from devis_batiment.storage import Database


class QuoteService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_quote(self, quote_input: QuoteInput, estimate: QuoteEstimate) -> int:
        return self.database.insert_quote(quote_input, estimate)

    def list_quotes(self) -> list[dict[str, object]]:
        return self.database.fetch_quotes()


class AdminService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_pricing_profile(
        self,
        building_type: str,
        finish_level: str,
        base_price_per_m2: float,
    ) -> None:
        self.database.upsert_pricing_profile(
            building_type,
            finish_level,
            float(base_price_per_m2),
        )

    def save_adjustment_rule(self, category: str, rule_key: str, multiplier: float) -> None:
        self.database.upsert_adjustment_rule(category, rule_key, float(multiplier))

    def save_breakdown_rule(self, lot_name: str, percentage: float) -> None:
        self.database.upsert_breakdown_rule(lot_name, float(percentage))

    def list_pricing_profiles(self) -> list[dict[str, object]]:
        return self.database.fetch_pricing_profiles()

    def list_adjustment_rules(self) -> list[dict[str, object]]:
        return self.database.fetch_adjustment_rules()

    def list_breakdown_rules(self) -> list[dict[str, object]]:
        return self.database.fetch_breakdown_rules()
