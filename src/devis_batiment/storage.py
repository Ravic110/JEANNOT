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
