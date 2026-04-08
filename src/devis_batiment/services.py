from __future__ import annotations

from devis_batiment.calculator import EstimateCalculator
from devis_batiment.config import DEFAULT_ADJUSTMENT_RULES, DEFAULT_BREAKDOWN_RULES, DEFAULT_PRICING_PROFILES
from devis_batiment.models import QuoteEstimate, QuoteInput
from devis_batiment.storage import Database


class QuoteService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_quote(self, quote_input: QuoteInput, estimate: QuoteEstimate) -> int:
        return self.database.insert_quote(quote_input, estimate)

    def list_quotes(self) -> list[dict[str, object]]:
        return self.database.fetch_quotes()

    def search_quotes(self, search_term: str) -> list[dict[str, object]]:
        return self.database.search_quotes(search_term)

    def duplicate_quote(self, quote_id: int) -> int:
        payload = self.database.fetch_quote_payload(quote_id)
        quote_input = QuoteInput(**payload["input"])
        estimate = QuoteEstimate(
            total_amount=payload["estimate"]["total_amount"],
            applied_multipliers=payload["estimate"]["applied_multipliers"],
            breakdown=payload["estimate"]["breakdown"],
        )
        return self.database.insert_quote(quote_input, estimate)


class AdminService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def seed_defaults_if_empty(self) -> None:
        """Insère les données de référence par défaut si la base est vide."""
        if not self.database.fetch_pricing_profiles():
            for row in DEFAULT_PRICING_PROFILES:
                self.database.upsert_pricing_profile(
                    str(row["building_type"]),
                    str(row["finish_level"]),
                    float(row["base_price_per_m2"]),
                )
        if not self.database.fetch_adjustment_rules():
            for row in DEFAULT_ADJUSTMENT_RULES:
                self.database.upsert_adjustment_rule(
                    str(row["category"]),
                    str(row["rule_key"]),
                    float(row["multiplier"]),
                )
        if not self.database.fetch_breakdown_rules():
            for row in DEFAULT_BREAKDOWN_RULES:
                self.database.upsert_breakdown_rule(
                    str(row["lot_name"]),
                    float(row["percentage"]),
                )

    def delete_pricing_profile(self, building_type: str, finish_level: str) -> None:
        self.database.delete_pricing_profile(building_type, finish_level)

    def delete_adjustment_rule(self, category: str, rule_key: str) -> None:
        self.database.delete_adjustment_rule(category, rule_key)

    def delete_breakdown_rule(self, lot_name: str) -> None:
        self.database.delete_breakdown_rule(lot_name)

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


SETTING_KEYS = [
    "company_name",
    "company_address",
    "company_phone",
    "company_email",
    "currency",
    "quote_validity_days",
    "safety_margin_pct",
]

SETTING_DEFAULTS: dict[str, str] = {
    "company_name": "Jeannot Devis Bâtiment",
    "company_address": "",
    "company_phone": "",
    "company_email": "",
    "currency": "Ar",
    "quote_validity_days": "30",
    "safety_margin_pct": "0",
}


class SettingsService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get(self, key: str) -> str:
        return self.database.get_setting(key, SETTING_DEFAULTS.get(key, ""))

    def set(self, key: str, value: str) -> None:
        self.database.set_setting(key, value)

    def get_all(self) -> dict[str, str]:
        stored = self.database.get_all_settings()
        return {key: stored.get(key, SETTING_DEFAULTS.get(key, "")) for key in SETTING_KEYS}

    def save_all(self, values: dict[str, str]) -> None:
        for key, value in values.items():
            if key in SETTING_KEYS:
                self.database.set_setting(key, value)


class QuoteWorkflow:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_quote(self, quote_input: QuoteInput) -> tuple[int, QuoteEstimate]:
        pricing_profiles = {
            (row["building_type"], row["finish_level"]): row["base_price_per_m2"]
            for row in self.database.fetch_pricing_profiles()
        }
        adjustment_rules = {
            (row["category"], row["rule_key"]): row["multiplier"]
            for row in self.database.fetch_adjustment_rules()
        }
        breakdown_rules = {
            row["lot_name"]: row["percentage"]
            for row in self.database.fetch_breakdown_rules()
        }
        estimate = EstimateCalculator(
            pricing_profiles=pricing_profiles,
            adjustment_rules=adjustment_rules,
            breakdown_rules=breakdown_rules,
        ).calculate(quote_input)
        saved_id = self.database.insert_quote(quote_input, estimate)
        return saved_id, estimate
