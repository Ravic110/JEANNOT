from __future__ import annotations

import sqlite3
from pathlib import Path


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
