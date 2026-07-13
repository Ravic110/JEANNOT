from __future__ import annotations

from devis_batiment.config import (
    DEFAULT_ADJUSTMENT_RULES,
    DEFAULT_BREAKDOWN_RULES,
    DEFAULT_MATERIALS,
)
from devis_batiment.models import MaterialLine, QuoteEstimate, QuoteInput
from devis_batiment.services.calcul_btp import BtpQuoteCalculator
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
            materials=[MaterialLine(**line) for line in payload["estimate"].get("materials", [])],
            volume_m3=float(payload["estimate"].get("volume_m3", 0.0)),
        )
        return self.database.insert_quote(quote_input, estimate)


class AdminService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def seed_defaults_if_empty(self) -> None:
        """Insère les données de référence par défaut si la base est vide."""
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
        if not self.database.fetch_materials():
            for row in DEFAULT_MATERIALS:
                self.database.upsert_material(
                    str(row["name"]),
                    str(row["unit"]),
                    float(row["unit_price"]),
                )

    def delete_adjustment_rule(self, category: str, rule_key: str) -> None:
        self.database.delete_adjustment_rule(category, rule_key)

    def delete_breakdown_rule(self, lot_name: str) -> None:
        self.database.delete_breakdown_rule(lot_name)

    def delete_material(self, name: str) -> None:
        self.database.delete_material(name)

    def save_adjustment_rule(self, category: str, rule_key: str, multiplier: float) -> None:
        self.database.upsert_adjustment_rule(category, rule_key, float(multiplier))

    def save_breakdown_rule(self, lot_name: str, percentage: float) -> None:
        self.database.upsert_breakdown_rule(lot_name, float(percentage))

    def save_material(self, name: str, unit: str, unit_price: float) -> None:
        self.database.upsert_material(name, unit, float(unit_price))

    def list_adjustment_rules(self) -> list[dict[str, object]]:
        return self.database.fetch_adjustment_rules()

    def list_breakdown_rules(self) -> list[dict[str, object]]:
        return self.database.fetch_breakdown_rules()

    def list_materials(self) -> list[dict[str, object]]:
        return self.database.fetch_materials()


class ClientService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_client(self, name: str, contact: str) -> int:
        return self.database.insert_client(name, contact)

    def list_clients(self) -> list[dict[str, object]]:
        return self.database.fetch_clients()

    def delete_client(self, client_id: int) -> None:
        self.database.delete_client(client_id)


class ProjectService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_project(
        self,
        client_name: str,
        client_contact: str,
        project_name: str,
        project_type: str,
        location: str,
        notes: str,
    ) -> int:
        client_id = self.database.insert_client(client_name, client_contact)
        return self.database.insert_project(client_id, project_name, project_type, location, notes)

    def list_projects(self) -> list[dict[str, object]]:
        return self.database.fetch_projects()

    def delete_project(self, project_id: int) -> None:
        self.database.delete_project(project_id)


SETTING_KEYS = [
    "company_name",
    "company_address",
    "company_phone",
    "company_email",
    "company_logo",
    "currency",
    "quote_validity_days",
    "safety_margin_pct",
]

SETTING_DEFAULTS: dict[str, str] = {
    "company_name": "SmartBTP Devis Desktop",
    "company_address": "",
    "company_phone": "",
    "company_email": "",
    "company_logo": "",
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
        material_prices = {
            row["name"]: {
                "unit": row["unit"],
                "unit_price": row["unit_price"],
            }
            for row in self.database.fetch_materials()
        }
        adjustment_rules = {
            (str(row["category"]), str(row["rule_key"])): float(row["multiplier"])
            for row in self.database.fetch_adjustment_rules()
        }
        breakdown_rules = {
            row["lot_name"]: row["percentage"]
            for row in self.database.fetch_breakdown_rules()
        }
        safety_margin_pct = float(self.database.get_setting("safety_margin_pct", "0"))

        estimate = BtpQuoteCalculator(
            material_prices=material_prices,
            adjustment_rules=adjustment_rules,
            breakdown_rules=breakdown_rules,
            safety_margin_pct=safety_margin_pct,
        ).calculate(quote_input)

        saved_id = self.database.insert_quote(quote_input, estimate)
        return saved_id, estimate
