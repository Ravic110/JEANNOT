from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from devis_batiment.models import QuoteEstimate, QuoteInput


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    def initialize(self) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS pricing_profiles (
                    id INTEGER PRIMARY KEY,
                    building_type TEXT NOT NULL,
                    finish_level TEXT NOT NULL,
                    base_price_per_m2 REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS adjustment_rules (
                    id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    rule_key TEXT NOT NULL,
                    multiplier REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS breakdown_rules (
                    id INTEGER PRIMARY KEY,
                    lot_name TEXT NOT NULL,
                    percentage REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    total_amount REAL NOT NULL
                );
                """
            )

    def list_tables(self) -> list[str]:
        with sqlite3.connect(self.path) as connection:
            rows = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()
        return [row[0] for row in rows]

    def insert_quote(self, quote_input: QuoteInput, estimate: QuoteEstimate) -> int:
        payload = {
            "input": asdict(quote_input),
            "estimate": {
                "total_amount": estimate.total_amount,
                "applied_multipliers": estimate.applied_multipliers,
                "breakdown": estimate.breakdown,
            },
        }
        with sqlite3.connect(self.path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO quotes(created_at, client_name, payload_json, total_amount)
                VALUES (?, ?, ?, ?)
                """,
                (
                    datetime.now(UTC).isoformat(),
                    quote_input.client_name,
                    json.dumps(payload),
                    estimate.total_amount,
                ),
            )
            return int(cursor.lastrowid)

    def fetch_quotes(self) -> list[dict[str, object]]:
        with sqlite3.connect(self.path) as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, client_name, total_amount
                FROM quotes
                ORDER BY id DESC
                """
            ).fetchall()
        return [
            {
                "id": row[0],
                "created_at": row[1],
                "client_name": row[2],
                "total_amount": row[3],
            }
            for row in rows
        ]

    def fetch_quote_payload(self, quote_id: int) -> dict[str, object]:
        with sqlite3.connect(self.path) as connection:
            row = connection.execute(
                "SELECT payload_json FROM quotes WHERE id = ?",
                (quote_id,),
            ).fetchone()
        if row is None:
            raise LookupError(f"Unknown quote id: {quote_id}")
        return json.loads(row[0])

    def search_quotes(self, search_term: str) -> list[dict[str, object]]:
        term = f"%{search_term}%"
        with sqlite3.connect(self.path) as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, client_name, total_amount
                FROM quotes
                WHERE client_name LIKE ?
                ORDER BY id DESC
                """,
                (term,),
            ).fetchall()
        return [
            {
                "id": row[0],
                "created_at": row[1],
                "client_name": row[2],
                "total_amount": row[3],
            }
            for row in rows
        ]

    def upsert_pricing_profile(
        self,
        building_type: str,
        finish_level: str,
        base_price_per_m2: float,
    ) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT INTO pricing_profiles(building_type, finish_level, base_price_per_m2)
                VALUES (?, ?, ?)
                """,
                (building_type, finish_level, base_price_per_m2),
            )

    def upsert_adjustment_rule(self, category: str, rule_key: str, multiplier: float) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT INTO adjustment_rules(category, rule_key, multiplier)
                VALUES (?, ?, ?)
                """,
                (category, rule_key, multiplier),
            )

    def upsert_breakdown_rule(self, lot_name: str, percentage: float) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT INTO breakdown_rules(lot_name, percentage)
                VALUES (?, ?)
                """,
                (lot_name, percentage),
            )

    def fetch_pricing_profiles(self) -> list[dict[str, object]]:
        with sqlite3.connect(self.path) as connection:
            rows = connection.execute(
                "SELECT building_type, finish_level, base_price_per_m2 FROM pricing_profiles ORDER BY id"
            ).fetchall()
        return [
            {"building_type": row[0], "finish_level": row[1], "base_price_per_m2": row[2]}
            for row in rows
        ]

    def fetch_adjustment_rules(self) -> list[dict[str, object]]:
        with sqlite3.connect(self.path) as connection:
            rows = connection.execute(
                "SELECT category, rule_key, multiplier FROM adjustment_rules ORDER BY id"
            ).fetchall()
        return [
            {"category": row[0], "rule_key": row[1], "multiplier": row[2]}
            for row in rows
        ]

    def fetch_breakdown_rules(self) -> list[dict[str, object]]:
        with sqlite3.connect(self.path) as connection:
            rows = connection.execute(
                "SELECT lot_name, percentage FROM breakdown_rules ORDER BY id"
            ).fetchall()
        return [{"lot_name": row[0], "percentage": row[1]} for row in rows]
