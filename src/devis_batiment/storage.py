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
        # SQLite in-memory databases lose data between connections.
        # Keep a single persistent connection for the :memory: case.
        self._conn: sqlite3.Connection | None = (
            sqlite3.connect(":memory:", check_same_thread=False)
            if str(path) == ":memory:"
            else None
        )

    def _connect(self) -> sqlite3.Connection:
        if self._conn is not None:
            self._conn.execute("PRAGMA foreign_keys = ON")
            return self._conn
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS pricing_profiles (
                    id INTEGER PRIMARY KEY,
                    building_type TEXT NOT NULL,
                    finish_level TEXT NOT NULL,
                    base_price_per_m2 REAL NOT NULL,
                    UNIQUE(building_type, finish_level)
                );

                CREATE TABLE IF NOT EXISTS adjustment_rules (
                    id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    rule_key TEXT NOT NULL,
                    multiplier REAL NOT NULL,
                    UNIQUE(category, rule_key)
                );

                CREATE TABLE IF NOT EXISTS breakdown_rules (
                    id INTEGER PRIMARY KEY,
                    lot_name TEXT NOT NULL UNIQUE,
                    percentage REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    total_amount REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS quote_lines (
                    id INTEGER PRIMARY KEY,
                    quote_id INTEGER NOT NULL,
                    material_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    unit_price REAL NOT NULL,
                    line_total REAL NOT NULL,
                    FOREIGN KEY(quote_id) REFERENCES quotes(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    contact TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    client_id INTEGER NOT NULL,
                    project_name TEXT,
                    project_type TEXT NOT NULL,
                    location TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    unit TEXT NOT NULL,
                    unit_price REAL NOT NULL,
                    last_updated TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            # Migration douce : ajout des index uniques si absents (bases existantes)
            try:
                connection.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_pricing_profiles_key "
                    "ON pricing_profiles(building_type, finish_level)"
                )
                connection.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_adjustment_rules_key "
                    "ON adjustment_rules(category, rule_key)"
                )
                connection.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_breakdown_rules_lot "
                    "ON breakdown_rules(lot_name)"
                )
                connection.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_clients_name "
                    "ON clients(name)"
                )
                connection.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_materials_name "
                    "ON materials(name)"
                )
            except sqlite3.OperationalError:
                pass

    def list_tables(self) -> list[str]:
        with self._connect() as connection:
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

    def fetch_quotes(self) -> list[dict[str, object]]:
        with self._connect() as connection:
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
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM quotes WHERE id = ?",
                (quote_id,),
            ).fetchone()
        if row is None:
            raise LookupError(f"Unknown quote id: {quote_id}")
        return json.loads(row[0])

    def search_quotes(self, search_term: str) -> list[dict[str, object]]:
        term = f"%{search_term}%"
        with self._connect() as connection:
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
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO pricing_profiles(building_type, finish_level, base_price_per_m2)
                VALUES (?, ?, ?)
                ON CONFLICT(building_type, finish_level)
                DO UPDATE SET base_price_per_m2 = excluded.base_price_per_m2
                """,
                (building_type, finish_level, base_price_per_m2),
            )

    def delete_pricing_profile(self, building_type: str, finish_level: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM pricing_profiles WHERE building_type = ? AND finish_level = ?",
                (building_type, finish_level),
            )

    def upsert_adjustment_rule(self, category: str, rule_key: str, multiplier: float) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO adjustment_rules(category, rule_key, multiplier)
                VALUES (?, ?, ?)
                ON CONFLICT(category, rule_key)
                DO UPDATE SET multiplier = excluded.multiplier
                """,
                (category, rule_key, multiplier),
            )

    def delete_adjustment_rule(self, category: str, rule_key: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM adjustment_rules WHERE category = ? AND rule_key = ?",
                (category, rule_key),
            )

    def upsert_breakdown_rule(self, lot_name: str, percentage: float) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO breakdown_rules(lot_name, percentage)
                VALUES (?, ?)
                ON CONFLICT(lot_name)
                DO UPDATE SET percentage = excluded.percentage
                """,
                (lot_name, percentage),
            )

    def delete_breakdown_rule(self, lot_name: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM breakdown_rules WHERE lot_name = ?",
                (lot_name,),
            )

    def fetch_pricing_profiles(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT building_type, finish_level, base_price_per_m2 FROM pricing_profiles ORDER BY building_type, finish_level"
            ).fetchall()
        return [
            {"building_type": row[0], "finish_level": row[1], "base_price_per_m2": row[2]}
            for row in rows
        ]

    def fetch_adjustment_rules(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT category, rule_key, multiplier FROM adjustment_rules ORDER BY category, rule_key"
            ).fetchall()
        return [
            {"category": row[0], "rule_key": row[1], "multiplier": row[2]}
            for row in rows
        ]

    def fetch_breakdown_rules(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT lot_name, percentage FROM breakdown_rules ORDER BY id"
            ).fetchall()
        return [{"lot_name": row[0], "percentage": row[1]} for row in rows]

    def fetch_materials(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name, unit, unit_price FROM materials ORDER BY name"
            ).fetchall()
        return [
            {"name": row[0], "unit": row[1], "unit_price": row[2]}
            for row in rows
        ]

    def upsert_material(self, name: str, unit: str, unit_price: float) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO materials(name, unit, unit_price, last_updated) VALUES (?, ?, ?, datetime('now')) "
                "ON CONFLICT(name) DO UPDATE SET unit = excluded.unit, unit_price = excluded.unit_price, last_updated = excluded.last_updated",
                (name, unit, unit_price),
            )

    def delete_material(self, name: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM materials WHERE name = ?",
                (name,),
            )

    def insert_client(self, name: str, contact: str) -> int:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO clients(name, contact, created_at) VALUES (?, ?, datetime('now')) "
                "ON CONFLICT(name) DO UPDATE SET contact = excluded.contact",
                (name, contact),
            )
            row = connection.execute(
                "SELECT id FROM clients WHERE name = ?",
                (name,),
            ).fetchone()
        if row is None:
            raise LookupError(f"Impossible de créer le client {name}")
        return int(row[0])

    def fetch_clients(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, name, contact, created_at FROM clients ORDER BY created_at DESC"
            ).fetchall()
        return [
            {"id": row[0], "name": row[1], "contact": row[2], "created_at": row[3]}
            for row in rows
        ]

    def delete_client(self, client_id: int) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM clients WHERE id = ?",
                (client_id,),
            )

    def insert_project(
        self,
        client_id: int,
        project_name: str,
        project_type: str,
        location: str,
        notes: str,
    ) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO projects(client_id, project_name, project_type, location, notes, created_at) "
                "VALUES (?, ?, ?, ?, ?, datetime('now'))",
                (client_id, project_name, project_type, location, notes),
            )
            return int(cursor.lastrowid)

    def fetch_projects(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT p.id, c.name, p.project_name, p.project_type, p.location "
                "FROM projects p "
                "LEFT JOIN clients c ON c.id = p.client_id "
                "ORDER BY p.created_at DESC"
            ).fetchall()
        return [
            {
                "id": row[0],
                "client_name": row[1],
                "project_name": row[2],
                "project_type": row[3],
                "location": row[4],
            }
            for row in rows
        ]

    def delete_project(self, project_id: int) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM projects WHERE id = ?",
                (project_id,),
            )

    def count_quotes(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) FROM quotes"
            ).fetchone()
        return int(row[0]) if row is not None else 0

    def count_projects(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) FROM projects"
            ).fetchone()
        return int(row[0]) if row is not None else 0

    def sum_quote_amounts(self) -> float:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COALESCE(SUM(total_amount), 0) FROM quotes"
            ).fetchone()
        return float(row[0]) if row is not None else 0.0

    def fetch_recent_quotes(self, limit: int = 5) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, created_at, client_name, total_amount FROM quotes ORDER BY created_at DESC LIMIT ?",
                (limit,),
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

    def insert_quote(self, quote_input: QuoteInput, estimate: QuoteEstimate) -> int:
        payload = {
            "input": asdict(quote_input),
            "estimate": {
                "total_amount": estimate.total_amount,
                "applied_multipliers": estimate.applied_multipliers,
                "breakdown": estimate.breakdown,
                "materials": [asdict(line) for line in estimate.materials],
                "volume_m3": estimate.volume_m3,
            },
        }
        with self._connect() as connection:
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
            quote_id = int(cursor.lastrowid)
            for line in estimate.materials:
                connection.execute(
                    "INSERT INTO quote_lines(quote_id, material_name, quantity, unit, unit_price, line_total) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (quote_id, line.name, line.quantity, line.unit, line.unit_price, line.line_total),
                )
            return quote_id

    def get_setting(self, key: str, default: str = "") -> str:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
        return row[0] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO settings(key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def get_all_settings(self) -> dict[str, str]:
        with self._connect() as connection:
            rows = connection.execute("SELECT key, value FROM settings").fetchall()
        return {row[0]: row[1] for row in rows}
