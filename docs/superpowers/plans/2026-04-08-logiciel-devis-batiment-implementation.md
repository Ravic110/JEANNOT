# Logiciel Devis Batiment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the version 1 desktop application that lets internal staff create approximate building quotes, manage pricing parameters, and review quote history offline.

**Architecture:** Use a small Python desktop application with PySide6 for the user interface, sqlite3 for local storage, and a pure-Python calculation engine isolated from UI code. Keep the code split into focused modules: domain models, persistence, pricing logic, application services, and desktop screens.

**Tech Stack:** Python 3.12, PySide6, sqlite3, pytest, pytest-qt, pathlib

---

## Proposed File Structure

- Create: `pyproject.toml`
- Create: `README.md`
- Create: `.gitignore`
- Create: `src/devis_batiment/__init__.py`
- Create: `src/devis_batiment/app.py`
- Create: `src/devis_batiment/config.py`
- Create: `src/devis_batiment/models.py`
- Create: `src/devis_batiment/storage.py`
- Create: `src/devis_batiment/calculator.py`
- Create: `src/devis_batiment/services.py`
- Create: `src/devis_batiment/ui/main_window.py`
- Create: `src/devis_batiment/ui/quote_form.py`
- Create: `src/devis_batiment/ui/quote_result.py`
- Create: `src/devis_batiment/ui/history_view.py`
- Create: `src/devis_batiment/ui/admin_view.py`
- Create: `tests/test_smoke.py`
- Create: `tests/test_storage.py`
- Create: `tests/test_calculator.py`
- Create: `tests/test_services.py`
- Create: `tests/test_ui_smoke.py`

## Implementation Notes

- Start by creating a Git repository because the current workspace is not one yet. Every commit step below assumes `git init` has already been run.
- Use sqlite tables for `pricing_profiles`, `adjustment_rules`, `breakdown_rules`, and `quotes`.
- Keep calculation rules data-driven so the administrator can update values without code changes.
- Use the built-in `sqlite3` module first. Do not add an ORM in version 1.
- The desktop UI should have four tabs: `Nouveau devis`, `Resultat`, `Historique`, and `Administration`.

### Task 1: Bootstrap the project and test runner

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `src/devis_batiment/__init__.py`
- Create: `src/devis_batiment/app.py`
- Test: `tests/test_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
from devis_batiment.app import build_app_metadata


def test_build_app_metadata_returns_expected_defaults():
    metadata = build_app_metadata()

    assert metadata["app_name"] == "Jeannot Devis Batiment"
    assert metadata["database_name"] == "devis_batiment.db"
    assert metadata["currency"] == "MGA"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError` or `cannot import name 'build_app_metadata'`

- [ ] **Step 3: Write minimal implementation**

`pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "jeannot-devis-batiment"
version = "0.1.0"
description = "Desktop estimator for approximate building quotes"
requires-python = ">=3.12"
dependencies = [
  "PySide6>=6.8,<7.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0,<9.0",
  "pytest-qt>=4.4,<5.0",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

`.gitignore`
```gitignore
__pycache__/
.pytest_cache/
.venv/
dist/
build/
*.pyc
*.pyo
*.pyd
*.db
```

`README.md`
```md
# Jeannot Devis Batiment

Application desktop pour produire des devis approximatifs de construction.
```

`src/devis_batiment/__init__.py`
```python
__all__ = ["__version__"]

__version__ = "0.1.0"
```

`src/devis_batiment/app.py`
```python
from __future__ import annotations


def build_app_metadata() -> dict[str, str]:
    return {
        "app_name": "Jeannot Devis Batiment",
        "database_name": "devis_batiment.db",
        "currency": "MGA",
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git init
git add pyproject.toml .gitignore README.md src/devis_batiment/__init__.py src/devis_batiment/app.py tests/test_smoke.py
git commit -m "chore: bootstrap desktop estimator project"
```

### Task 2: Create domain models and sqlite schema bootstrap

**Files:**
- Create: `src/devis_batiment/config.py`
- Create: `src/devis_batiment/models.py`
- Create: `src/devis_batiment/storage.py`
- Test: `tests/test_storage.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from devis_batiment.storage import Database


def test_database_initialize_creates_expected_tables(tmp_path: Path):
    database = Database(tmp_path / "test.db")

    database.initialize()

    table_names = database.list_tables()
    assert table_names == [
        "adjustment_rules",
        "breakdown_rules",
        "pricing_profiles",
        "quotes",
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_storage.py::test_database_initialize_creates_expected_tables -v`
Expected: FAIL with `ModuleNotFoundError` or `AttributeError: 'Database' object has no attribute 'initialize'`

- [ ] **Step 3: Write minimal implementation**

`src/devis_batiment/config.py`
```python
from __future__ import annotations

from pathlib import Path


def default_database_path() -> Path:
    return Path.cwd() / "devis_batiment.db"
```

`src/devis_batiment/models.py`
```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class QuoteInput:
    client_name: str
    client_contact: str
    building_type: str
    location: str
    surface_m2: float
    floors: int
    structure_type: str
    roof_type: str
    room_count: int
    finish_level: str
    complexity: str
    notes: str = ""
```

`src/devis_batiment/storage.py`
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_storage.py::test_database_initialize_creates_expected_tables -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/config.py src/devis_batiment/models.py src/devis_batiment/storage.py tests/test_storage.py
git commit -m "feat: add domain model and sqlite bootstrap"
```

### Task 3: Build the calculation engine

**Files:**
- Create: `src/devis_batiment/calculator.py`
- Modify: `src/devis_batiment/models.py`
- Test: `tests/test_calculator.py`

- [ ] **Step 1: Write the failing test**

```python
from devis_batiment.calculator import EstimateCalculator
from devis_batiment.models import QuoteInput


def test_estimate_calculator_applies_base_price_adjustments_and_breakdown():
    quote_input = QuoteInput(
        client_name="Client Demo",
        client_contact="0340000000",
        building_type="Villa",
        location="Antananarivo",
        surface_m2=120,
        floors=1,
        structure_type="Beton arme",
        roof_type="Tuile",
        room_count=5,
        finish_level="Standard",
        complexity="Normal",
    )

    calculator = EstimateCalculator(
        pricing_profiles={("Villa", "Standard"): 800_000},
        adjustment_rules={
            ("location", "Antananarivo"): 1.0,
            ("structure_type", "Beton arme"): 1.05,
            ("roof_type", "Tuile"): 1.08,
            ("complexity", "Normal"): 1.0,
            ("floors", "1"): 1.0,
        },
        breakdown_rules={
            "Fondations": 0.20,
            "Structure": 0.30,
            "Toiture": 0.15,
            "Finitions": 0.25,
            "Divers": 0.10,
        },
    )

    estimate = calculator.calculate(quote_input)

    assert round(estimate.total_amount, 2) == 108_864_000.00
    assert estimate.breakdown["Structure"] == 32_659_200.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_calculator.py::test_estimate_calculator_applies_base_price_adjustments_and_breakdown -v`
Expected: FAIL with `ModuleNotFoundError` or `cannot import name 'EstimateCalculator'`

- [ ] **Step 3: Write minimal implementation**

`src/devis_batiment/models.py`
```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class QuoteInput:
    client_name: str
    client_contact: str
    building_type: str
    location: str
    surface_m2: float
    floors: int
    structure_type: str
    roof_type: str
    room_count: int
    finish_level: str
    complexity: str
    notes: str = ""


@dataclass(slots=True)
class QuoteEstimate:
    total_amount: float
    applied_multipliers: dict[str, float]
    breakdown: dict[str, float]
```

`src/devis_batiment/calculator.py`
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_calculator.py::test_estimate_calculator_applies_base_price_adjustments_and_breakdown -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/models.py src/devis_batiment/calculator.py tests/test_calculator.py
git commit -m "feat: add estimate calculation engine"
```

### Task 4: Persist pricing rules and quote history

**Files:**
- Modify: `src/devis_batiment/storage.py`
- Create: `src/devis_batiment/services.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from devis_batiment.models import QuoteEstimate, QuoteInput
from devis_batiment.services import QuoteService
from devis_batiment.storage import Database


def test_quote_service_saves_and_lists_quotes(tmp_path: Path):
    database = Database(tmp_path / "quotes.db")
    database.initialize()

    service = QuoteService(database)
    quote_input = QuoteInput(
        client_name="Mme Ranaivo",
        client_contact="0321111111",
        building_type="Villa",
        location="Toamasina",
        surface_m2=95,
        floors=1,
        structure_type="Beton arme",
        roof_type="Bac acier",
        room_count=4,
        finish_level="Economique",
        complexity="Simple",
    )
    estimate = QuoteEstimate(
        total_amount=56_000_000.0,
        applied_multipliers={"location": 1.02},
        breakdown={"Fondations": 11_200_000.0},
    )

    saved_id = service.save_quote(quote_input, estimate)
    rows = service.list_quotes()

    assert saved_id == 1
    assert rows[0]["client_name"] == "Mme Ranaivo"
    assert rows[0]["total_amount"] == 56_000_000.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_services.py::test_quote_service_saves_and_lists_quotes -v`
Expected: FAIL with `cannot import name 'QuoteService'` or missing methods

- [ ] **Step 3: Write minimal implementation**

`src/devis_batiment/storage.py`
```python
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, UTC
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
```

`src/devis_batiment/services.py`
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_services.py::test_quote_service_saves_and_lists_quotes -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/storage.py src/devis_batiment/services.py tests/test_services.py
git commit -m "feat: persist quote history"
```

### Task 5: Add pricing administration workflows

**Files:**
- Modify: `src/devis_batiment/storage.py`
- Modify: `src/devis_batiment/services.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from devis_batiment.services import AdminService
from devis_batiment.storage import Database


def test_admin_service_saves_and_reads_reference_rules(tmp_path: Path):
    database = Database(tmp_path / "admin.db")
    database.initialize()

    service = AdminService(database)
    service.save_pricing_profile("Villa", "Standard", 800_000)
    service.save_adjustment_rule("roof_type", "Tuile", 1.08)
    service.save_breakdown_rule("Fondations", 0.20)

    assert service.list_pricing_profiles() == [
        {"building_type": "Villa", "finish_level": "Standard", "base_price_per_m2": 800_000.0}
    ]
    assert service.list_adjustment_rules()[0]["rule_key"] == "Tuile"
    assert service.list_breakdown_rules()[0]["lot_name"] == "Fondations"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_services.py::test_admin_service_saves_and_reads_reference_rules -v`
Expected: FAIL with `cannot import name 'AdminService'` or missing methods

- [ ] **Step 3: Write minimal implementation**

`src/devis_batiment/storage.py`
```python
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, UTC
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
            {"id": row[0], "created_at": row[1], "client_name": row[2], "total_amount": row[3]}
            for row in rows
        ]

    def upsert_pricing_profile(self, building_type: str, finish_level: str, base_price_per_m2: float) -> None:
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
```

`src/devis_batiment/services.py`
```python
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

    def save_pricing_profile(self, building_type: str, finish_level: str, base_price_per_m2: float) -> None:
        self.database.upsert_pricing_profile(building_type, finish_level, float(base_price_per_m2))

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_services.py::test_admin_service_saves_and_reads_reference_rules -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/storage.py src/devis_batiment/services.py tests/test_services.py
git commit -m "feat: add pricing administration services"
```

### Task 6: Wire the quote workflow service

**Files:**
- Modify: `src/devis_batiment/services.py`
- Modify: `src/devis_batiment/storage.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from devis_batiment.models import QuoteInput
from devis_batiment.services import AdminService, QuoteWorkflow
from devis_batiment.storage import Database


def test_quote_workflow_uses_reference_data_and_persists_quote(tmp_path: Path):
    database = Database(tmp_path / "workflow.db")
    database.initialize()

    admin = AdminService(database)
    admin.save_pricing_profile("Villa", "Standard", 800_000)
    admin.save_adjustment_rule("location", "Antananarivo", 1.0)
    admin.save_adjustment_rule("structure_type", "Beton arme", 1.05)
    admin.save_adjustment_rule("roof_type", "Tuile", 1.08)
    admin.save_adjustment_rule("complexity", "Normal", 1.0)
    admin.save_adjustment_rule("floors", "1", 1.0)
    admin.save_breakdown_rule("Fondations", 0.20)
    admin.save_breakdown_rule("Structure", 0.30)
    admin.save_breakdown_rule("Toiture", 0.15)
    admin.save_breakdown_rule("Finitions", 0.25)
    admin.save_breakdown_rule("Divers", 0.10)

    workflow = QuoteWorkflow(database)
    saved_id, estimate = workflow.create_quote(
        QuoteInput(
            client_name="M. Rakoto",
            client_contact="0332222222",
            building_type="Villa",
            location="Antananarivo",
            surface_m2=120,
            floors=1,
            structure_type="Beton arme",
            roof_type="Tuile",
            room_count=5,
            finish_level="Standard",
            complexity="Normal",
        )
    )

    assert saved_id == 1
    assert round(estimate.total_amount, 2) == 108_864_000.00
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_services.py::test_quote_workflow_uses_reference_data_and_persists_quote -v`
Expected: FAIL with `cannot import name 'QuoteWorkflow'`

- [ ] **Step 3: Write minimal implementation**

`src/devis_batiment/storage.py`
```python
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, UTC
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
            {"id": row[0], "created_at": row[1], "client_name": row[2], "total_amount": row[3]}
            for row in rows
        ]

    def upsert_pricing_profile(self, building_type: str, finish_level: str, base_price_per_m2: float) -> None:
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
```

`src/devis_batiment/services.py`
```python
from __future__ import annotations

from devis_batiment.calculator import EstimateCalculator
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

    def save_pricing_profile(self, building_type: str, finish_level: str, base_price_per_m2: float) -> None:
        self.database.upsert_pricing_profile(building_type, finish_level, float(base_price_per_m2))

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
            row["lot_name"]: row["percentage"] for row in self.database.fetch_breakdown_rules()
        }
        estimate = EstimateCalculator(
            pricing_profiles=pricing_profiles,
            adjustment_rules=adjustment_rules,
            breakdown_rules=breakdown_rules,
        ).calculate(quote_input)
        saved_id = self.database.insert_quote(quote_input, estimate)
        return saved_id, estimate
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_services.py::test_quote_workflow_uses_reference_data_and_persists_quote -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/storage.py src/devis_batiment/services.py tests/test_services.py
git commit -m "feat: add end-to-end quote workflow"
```

### Task 7: Build the desktop UI shell and quote form

**Files:**
- Create: `src/devis_batiment/ui/main_window.py`
- Create: `src/devis_batiment/ui/quote_form.py`
- Create: `src/devis_batiment/ui/quote_result.py`
- Modify: `src/devis_batiment/app.py`
- Test: `tests/test_ui_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
from PySide6.QtWidgets import QApplication

from devis_batiment.ui.main_window import MainWindow


def test_main_window_contains_core_tabs(qtbot):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    qtbot.addWidget(window)

    labels = [window.tabs.tabText(index) for index in range(window.tabs.count())]
    assert labels == ["Nouveau devis", "Resultat", "Historique", "Administration"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui_smoke.py::test_main_window_contains_core_tabs -v`
Expected: FAIL with `ModuleNotFoundError` or `cannot import name 'MainWindow'`

- [ ] **Step 3: Write minimal implementation**

`src/devis_batiment/ui/quote_form.py`
```python
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLineEdit, QSpinBox, QWidget


class QuoteFormWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.client_name = QLineEdit()
        self.surface_m2 = QLineEdit()
        self.floors = QSpinBox()
        self.floors.setMinimum(0)
        self.floors.setMaximum(50)
        layout.addRow("Client", self.client_name)
        layout.addRow("Surface (m2)", self.surface_m2)
        layout.addRow("Etages", self.floors)
```

`src/devis_batiment/ui/quote_result.py`
```python
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class QuoteResultWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Le resultat du devis apparaitra ici."))
```

`src/devis_batiment/ui/main_window.py`
```python
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMainWindow, QTabWidget

from devis_batiment.ui.quote_form import QuoteFormWidget
from devis_batiment.ui.quote_result import QuoteResultWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jeannot Devis Batiment")
        self.tabs = QTabWidget()
        self.tabs.addTab(QuoteFormWidget(), "Nouveau devis")
        self.tabs.addTab(QuoteResultWidget(), "Resultat")
        self.tabs.addTab(QLabel("Historique"), "Historique")
        self.tabs.addTab(QLabel("Administration"), "Administration")
        self.setCentralWidget(self.tabs)
```

`src/devis_batiment/app.py`
```python
from __future__ import annotations

from PySide6.QtWidgets import QApplication

from devis_batiment.ui.main_window import MainWindow


def build_app_metadata() -> dict[str, str]:
    return {
        "app_name": "Jeannot Devis Batiment",
        "database_name": "devis_batiment.db",
        "currency": "MGA",
    }


def run() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ui_smoke.py::test_main_window_contains_core_tabs -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/ui/main_window.py src/devis_batiment/ui/quote_form.py src/devis_batiment/ui/quote_result.py src/devis_batiment/app.py tests/test_ui_smoke.py
git commit -m "feat: add desktop shell and quote form"
```

### Task 8: Add history and administration screens

**Files:**
- Create: `src/devis_batiment/ui/history_view.py`
- Create: `src/devis_batiment/ui/admin_view.py`
- Modify: `src/devis_batiment/ui/main_window.py`
- Test: `tests/test_ui_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
from PySide6.QtWidgets import QApplication

from devis_batiment.ui.admin_view import AdminView
from devis_batiment.ui.history_view import HistoryView


def test_admin_and_history_views_expose_main_tables(qtbot):
    app = QApplication.instance() or QApplication([])
    admin_view = AdminView()
    history_view = HistoryView()
    qtbot.addWidget(admin_view)
    qtbot.addWidget(history_view)

    assert admin_view.pricing_table.columnCount() == 3
    assert history_view.quote_table.columnCount() == 4
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui_smoke.py::test_admin_and_history_views_expose_main_tables -v`
Expected: FAIL with `ModuleNotFoundError` or missing attributes

- [ ] **Step 3: Write minimal implementation**

`src/devis_batiment/ui/history_view.py`
```python
from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QVBoxLayout, QWidget


class HistoryView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.quote_table = QTableWidget(0, 4)
        self.quote_table.setHorizontalHeaderLabels(["ID", "Date", "Client", "Montant"])
        layout.addWidget(self.quote_table)
```

`src/devis_batiment/ui/admin_view.py`
```python
from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QTabWidget, QVBoxLayout, QWidget


class AdminView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.pricing_table = QTableWidget(0, 3)
        self.pricing_table.setHorizontalHeaderLabels(["Type", "Finition", "Prix/m2"])
        self.adjustment_table = QTableWidget(0, 3)
        self.adjustment_table.setHorizontalHeaderLabels(["Categorie", "Cle", "Coefficient"])
        self.breakdown_table = QTableWidget(0, 2)
        self.breakdown_table.setHorizontalHeaderLabels(["Lot", "Pourcentage"])
        self.tabs.addTab(self.pricing_table, "Prix")
        self.tabs.addTab(self.adjustment_table, "Coefficients")
        self.tabs.addTab(self.breakdown_table, "Repartition")
        layout.addWidget(self.tabs)
```

`src/devis_batiment/ui/main_window.py`
```python
from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from devis_batiment.ui.admin_view import AdminView
from devis_batiment.ui.history_view import HistoryView
from devis_batiment.ui.quote_form import QuoteFormWidget
from devis_batiment.ui.quote_result import QuoteResultWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jeannot Devis Batiment")
        self.tabs = QTabWidget()
        self.tabs.addTab(QuoteFormWidget(), "Nouveau devis")
        self.tabs.addTab(QuoteResultWidget(), "Resultat")
        self.tabs.addTab(HistoryView(), "Historique")
        self.tabs.addTab(AdminView(), "Administration")
        self.setCentralWidget(self.tabs)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ui_smoke.py::test_admin_and_history_views_expose_main_tables -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/ui/history_view.py src/devis_batiment/ui/admin_view.py src/devis_batiment/ui/main_window.py tests/test_ui_smoke.py
git commit -m "feat: add history and administration views"
```

### Task 9: Connect services to the UI and validate the full workflow

**Files:**
- Modify: `src/devis_batiment/ui/quote_form.py`
- Modify: `src/devis_batiment/ui/quote_result.py`
- Modify: `src/devis_batiment/ui/history_view.py`
- Modify: `src/devis_batiment/ui/admin_view.py`
- Modify: `src/devis_batiment/ui/main_window.py`
- Modify: `src/devis_batiment/app.py`
- Test: `tests/test_ui_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from PySide6.QtWidgets import QApplication

from devis_batiment.app import create_main_window


def test_create_main_window_bootstraps_database_and_services(tmp_path: Path, qtbot):
    app = QApplication.instance() or QApplication([])
    window = create_main_window(tmp_path / "desktop.db")
    qtbot.addWidget(window)

    assert window.database.path.name == "desktop.db"
    assert window.tabs.count() == 4
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui_smoke.py::test_create_main_window_bootstraps_database_and_services -v`
Expected: FAIL with `cannot import name 'create_main_window'`

- [ ] **Step 3: Write minimal implementation**

`src/devis_batiment/ui/main_window.py`
```python
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QTabWidget

from devis_batiment.services import AdminService, QuoteService, QuoteWorkflow
from devis_batiment.storage import Database
from devis_batiment.ui.admin_view import AdminView
from devis_batiment.ui.history_view import HistoryView
from devis_batiment.ui.quote_form import QuoteFormWidget
from devis_batiment.ui.quote_result import QuoteResultWidget


class MainWindow(QMainWindow):
    def __init__(self, database: Database | None = None) -> None:
        super().__init__()
        self.database = database or Database(Path(":memory:"))
        self.database.initialize()
        self.admin_service = AdminService(self.database)
        self.quote_service = QuoteService(self.database)
        self.quote_workflow = QuoteWorkflow(self.database)
        self.setWindowTitle("Jeannot Devis Batiment")
        self.tabs = QTabWidget()
        self.tabs.addTab(QuoteFormWidget(), "Nouveau devis")
        self.tabs.addTab(QuoteResultWidget(), "Resultat")
        self.tabs.addTab(HistoryView(), "Historique")
        self.tabs.addTab(AdminView(), "Administration")
        self.setCentralWidget(self.tabs)
```

`src/devis_batiment/app.py`
```python
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication

from devis_batiment.config import default_database_path
from devis_batiment.storage import Database
from devis_batiment.ui.main_window import MainWindow


def build_app_metadata() -> dict[str, str]:
    return {
        "app_name": "Jeannot Devis Batiment",
        "database_name": "devis_batiment.db",
        "currency": "MGA",
    }


def create_main_window(database_path: Path | None = None) -> MainWindow:
    path = database_path or default_database_path()
    database = Database(path)
    database.initialize()
    return MainWindow(database)


def run() -> int:
    app = QApplication.instance() or QApplication([])
    window = create_main_window()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ui_smoke.py::test_create_main_window_bootstraps_database_and_services -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/ui/main_window.py src/devis_batiment/app.py tests/test_ui_smoke.py
git commit -m "feat: bootstrap services into desktop UI"
```

### Task 10: Add history search and quote duplication

**Files:**
- Modify: `src/devis_batiment/storage.py`
- Modify: `src/devis_batiment/services.py`
- Modify: `src/devis_batiment/ui/history_view.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from devis_batiment.models import QuoteEstimate, QuoteInput
from devis_batiment.services import QuoteService
from devis_batiment.storage import Database


def test_quote_service_can_search_and_duplicate_quotes(tmp_path: Path):
    database = Database(tmp_path / "history.db")
    database.initialize()
    service = QuoteService(database)
    quote_input = QuoteInput(
        client_name="M. Rakoto",
        client_contact="0332222222",
        building_type="Villa",
        location="Antananarivo",
        surface_m2=120,
        floors=1,
        structure_type="Beton arme",
        roof_type="Tuile",
        room_count=5,
        finish_level="Standard",
        complexity="Normal",
    )
    estimate = QuoteEstimate(
        total_amount=108_864_000.0,
        applied_multipliers={"location": 1.0},
        breakdown={"Fondations": 21_772_800.0},
    )

    original_id = service.save_quote(quote_input, estimate)
    duplicated_id = service.duplicate_quote(original_id)
    results = service.search_quotes("Rakoto")

    assert duplicated_id == 2
    assert len(results) == 2
    assert results[0]["client_name"] == "M. Rakoto"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_services.py::test_quote_service_can_search_and_duplicate_quotes -v`
Expected: FAIL with missing `duplicate_quote` or `search_quotes`

- [ ] **Step 3: Write minimal implementation**

`src/devis_batiment/storage.py`
```python
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, UTC
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
            {"id": row[0], "created_at": row[1], "client_name": row[2], "total_amount": row[3]}
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
            {"id": row[0], "created_at": row[1], "client_name": row[2], "total_amount": row[3]}
            for row in rows
        ]
```

`src/devis_batiment/services.py`
```python
from __future__ import annotations

from devis_batiment.calculator import EstimateCalculator
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

    def save_pricing_profile(self, building_type: str, finish_level: str, base_price_per_m2: float) -> None:
        self.database.upsert_pricing_profile(building_type, finish_level, float(base_price_per_m2))

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
            row["lot_name"]: row["percentage"] for row in self.database.fetch_breakdown_rules()
        }
        estimate = EstimateCalculator(
            pricing_profiles=pricing_profiles,
            adjustment_rules=adjustment_rules,
            breakdown_rules=breakdown_rules,
        ).calculate(quote_input)
        saved_id = self.database.insert_quote(quote_input, estimate)
        return saved_id, estimate
```

`src/devis_batiment/ui/history_view.py`
```python
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QVBoxLayout, QWidget


class HistoryView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un client")
        self.duplicate_button = QPushButton("Dupliquer")
        filters.addWidget(self.search_input)
        filters.addWidget(self.duplicate_button)
        self.quote_table = QTableWidget(0, 4)
        self.quote_table.setHorizontalHeaderLabels(["ID", "Date", "Client", "Montant"])
        layout.addLayout(filters)
        layout.addWidget(self.quote_table)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_services.py::test_quote_service_can_search_and_duplicate_quotes -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/storage.py src/devis_batiment/services.py src/devis_batiment/ui/history_view.py tests/test_services.py
git commit -m "feat: add history search and quote duplication"
```

### Task 11: Full verification, packaging notes, and delivery checklist

**Files:**
- Modify: `README.md`
- Modify: `tests/test_smoke.py`
- Modify: `tests/test_storage.py`
- Modify: `tests/test_calculator.py`
- Modify: `tests/test_services.py`
- Modify: `tests/test_ui_smoke.py`

- [ ] **Step 1: Add a final smoke test for the default bootstrap**

```python
from pathlib import Path

from PySide6.QtWidgets import QApplication

from devis_batiment.app import create_main_window


def test_create_main_window_uses_default_database_name(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = QApplication.instance() or QApplication([])

    window = create_main_window()

    assert window.database.path.name == "devis_batiment.db"
    assert window.windowTitle() == "Jeannot Devis Batiment"
```

- [ ] **Step 2: Run the full test suite and verify green**

Run: `pytest -v`
Expected: PASS with all storage, calculator, service, and UI smoke tests green

- [ ] **Step 3: Update README with run instructions**

`README.md`
````md
# Jeannot Devis Batiment

Application desktop pour produire des devis approximatifs de construction.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Lancer l'application

```bash
python -m devis_batiment.app
```

## Lancer les tests

```bash
pytest -v
```
````

- [ ] **Step 4: Commit**

```bash
git add README.md tests/test_smoke.py tests/test_storage.py tests/test_calculator.py tests/test_services.py tests/test_ui_smoke.py
git commit -m "docs: finalize setup and verification instructions"
```
