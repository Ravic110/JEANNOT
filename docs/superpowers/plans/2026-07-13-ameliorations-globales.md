# Améliorations globales — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Supprimer le code mort « profils de prix », brancher l'export PDF et la réouverture de devis, rendre la devise et l'intégrité FK effectives, et remettre le dépôt/README en cohérence.

**Architecture:** Application desktop PySide6 en couches — `models` (dataclasses) → `storage` (SQLite) → `services` (logique métier) → `ui` (Qt). Le moteur de calcul reste `matériaux × volume` ([services/calcul_btp.py](../../../src/devis_batiment/services/calcul_btp.py)). Aucune refonte : on retire du code, on branche des signaux/boutons existants, on ajoute une méthode de service et un formatage devise partagé.

**Tech Stack:** Python 3.12+, PySide6 (Qt), SQLite (stdlib `sqlite3`), reportlab (PDF), pytest + pytest-qt.

## Global Constraints

- Python `>=3.12`.
- PySide6 : `PySide6_Essentials>=6.8,<7.0`.
- Nouvelle dépendance runtime : `reportlab>=4.0,<5.0`.
- Tests exécutés avec `QT_QPA_PLATFORM=offscreen`.
- Nom d'application partout : « Jeannot Devis Bâtiment ».
- Devise par défaut / fallback d'affichage : « Ar ».
- Moteur de calcul inchangé (`matériaux × volume`).
- Commits fréquents, un par tâche terminée.

---

## File Structure

- `src/devis_batiment/storage.py` — schéma SQLite : ajout `PRAGMA foreign_keys`, cascades, suppression méthodes `pricing_profiles`.
- `src/devis_batiment/config.py` — suppression `DEFAULT_PRICING_PROFILES`.
- `src/devis_batiment/services/__init__.py` — suppression méthodes pricing + seed ; ajout `QuoteService.load_quote` ; nom d'entreprise par défaut.
- `src/devis_batiment/ui/admin_view.py` — suppression onglet « Prix de base » ; nettoyage imports/code mort.
- `src/devis_batiment/ui/quote_result.py` — bouton export PDF ; formatage devise ; mémorisation du dernier résultat.
- `src/devis_batiment/ui/history_view.py` — émission double-clic ; formatage devise.
- `src/devis_batiment/ui/dashboard_view.py` — formatage devise.
- `src/devis_batiment/ui/main_window.py` — câblage réouverture + injection devise/settings ; nom fenêtre.
- `src/devis_batiment/app.py` — `build_app_metadata` nom app.
- `src/devis_batiment/utils/pdf.py` — nom d'entreprise par défaut.
- `pyproject.toml` — dépendance reportlab.
- `README.md` — structure + formule + PDF + note FK.
- `tests/*` — mise à jour (retrait pricing) + nouveaux tests.
- `devis_batiment.db` (racine) — suppression.

---

## Task 1 : Intégrité base de données (FK + cascades)

**Files:**
- Modify: `src/devis_batiment/storage.py`
- Test: `tests/test_storage.py`

**Interfaces:**
- Produces: `Database._connect()` active `PRAGMA foreign_keys = ON` ; schéma avec `projects.client_id → clients(id) ON DELETE CASCADE` et `quote_lines.quote_id → quotes(id) ON DELETE CASCADE`.

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter dans `tests/test_storage.py` :

```python
def test_deleting_client_cascades_to_projects(tmp_path: Path):
    database = Database(tmp_path / "cascade.db")
    database.initialize()

    client_id = database.insert_client("M. Rakoto", "0331111111")
    database.insert_project(client_id, "Villa", "Maison", "Antananarivo", "")

    assert len(database.fetch_projects()) == 1

    database.delete_client(client_id)

    assert database.fetch_projects() == []
    assert database.count_projects() == 0
```

- [ ] **Step 2: Lancer le test pour vérifier l'échec**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_storage.py::test_deleting_client_cascades_to_projects -v`
Expected: FAIL (le projet subsiste, `fetch_projects()` retourne 1 ligne car les FK ne sont pas appliquées).

- [ ] **Step 3: Activer les FK et les cascades**

Dans `src/devis_batiment/storage.py`, méthode `_connect`, activer le pragma sur chaque connexion retournée :

```python
    def _connect(self) -> sqlite3.Connection:
        if self._conn is not None:
            self._conn.execute("PRAGMA foreign_keys = ON")
            return self._conn
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
```

Dans le `CREATE TABLE ... projects`, remplacer la contrainte par :

```sql
                    FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
```

Dans le `CREATE TABLE ... quote_lines`, remplacer la contrainte par :

```sql
                    FOREIGN KEY(quote_id) REFERENCES quotes(id) ON DELETE CASCADE
```

- [ ] **Step 4: Lancer le test pour vérifier le succès**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_storage.py -v`
Expected: PASS (nouveau test + `test_database_initialize_creates_expected_tables`).

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/storage.py tests/test_storage.py
git commit -m "feat(storage): enforce foreign keys and cascade deletes

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2 : Supprimer le système « Profils de prix »

**Files:**
- Modify: `src/devis_batiment/storage.py`
- Modify: `src/devis_batiment/config.py`
- Modify: `src/devis_batiment/services/__init__.py`
- Modify: `src/devis_batiment/ui/admin_view.py`
- Test: `tests/test_storage.py`, `tests/test_services.py`

**Interfaces:**
- Produces: plus de table `pricing_profiles` ni de méthodes `*_pricing_profile(s)` ; `AdminService` sans API pricing ; onglet Admin réduit à « Coefficients » + « Répartition ».

- [ ] **Step 1: Mettre à jour les tests (retrait pricing)**

Dans `tests/test_storage.py`, retirer `"pricing_profiles"` de la liste attendue :

```python
    assert sorted(table_names) == sorted([
        "adjustment_rules",
        "breakdown_rules",
        "quotes",
        "quote_lines",
        "clients",
        "projects",
        "materials",
        "settings",
    ])
```

Dans `tests/test_services.py`, fonction `test_admin_service_saves_and_reads_reference_rules`, supprimer l'appel `service.save_pricing_profile(...)` et l'assertion `service.list_pricing_profiles() == [...]`. Le corps devient :

```python
def test_admin_service_saves_and_reads_reference_rules(tmp_path: Path):
    database = Database(tmp_path / "admin.db")
    database.initialize()

    service = AdminService(database)
    service.save_adjustment_rule("roof_type", "Tuile", 1.08)
    service.save_breakdown_rule("Fondations", 0.20)
    service.save_material("Ciment", "sacs 50kg", 45_000)

    assert service.list_adjustment_rules()[0]["rule_key"] == "Tuile"
    assert service.list_breakdown_rules()[0]["lot_name"] == "Fondations"
    assert len(service.list_materials()) >= 1
```

- [ ] **Step 2: Lancer les tests pour vérifier l'échec**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_storage.py tests/test_services.py -v`
Expected: FAIL (`test_database_initialize_creates_expected_tables` échoue car `pricing_profiles` existe encore ; les autres passent).

- [ ] **Step 3: Retirer le code pricing du storage**

Dans `src/devis_batiment/storage.py` :
- Supprimer le bloc `CREATE TABLE IF NOT EXISTS pricing_profiles (...)`.
- Supprimer la création d'index `idx_pricing_profiles_key`.
- Supprimer les méthodes `upsert_pricing_profile`, `delete_pricing_profile`, `fetch_pricing_profiles`.

- [ ] **Step 4: Retirer les données et services pricing**

Dans `src/devis_batiment/config.py` : supprimer la constante `DEFAULT_PRICING_PROFILES` (bloc complet).

Dans `src/devis_batiment/services/__init__.py` :
- Retirer `DEFAULT_PRICING_PROFILES` de l'import `from devis_batiment.config import (...)`.
- Dans `AdminService.seed_defaults_if_empty`, supprimer le bloc
  `if not self.database.fetch_pricing_profiles(): ...`.
- Supprimer les méthodes `delete_pricing_profile`, `save_pricing_profile`,
  `list_pricing_profiles`.

- [ ] **Step 5: Retirer l'onglet « Prix de base » de l'UI**

Dans `src/devis_batiment/ui/admin_view.py` :
- Supprimer la constante `BUILDING_TYPES` (lignes 30-38).
- Supprimer le bloc « Tab 1 : Profils de prix » (création `pricing_table` +
  `self.tabs.addTab(... "Prix de base")`).
- Dans `refresh`, supprimer l'appel `self._load_pricing()`.
- Supprimer les méthodes `_load_pricing`, `_add_pricing`, `_del_pricing`.
- Supprimer la classe `_PricingDialog`.
- Retirer de l'import `from devis_batiment.config import (...)` les noms devenus
  inutiles (`FINISH_LEVELS` n'est plus utilisé si présent uniquement pour le
  pricing — vérifier : il est aussi utilisé par `_AdjustmentDialog`? Non.
  `FINISH_LEVELS` n'est utilisé que par `_PricingDialog` → le retirer).

- [ ] **Step 6: Lancer toute la suite**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -v`
Expected: PASS (tous les tests, y compris `test_ui_smoke`).

- [ ] **Step 7: Vérifier l'app à la main (smoke)**

Run:
```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -c "
from PySide6.QtWidgets import QApplication
app = QApplication([])
from devis_batiment.app import create_main_window
w = create_main_window()
assert w.admin_view.tabs.count() == 2, w.admin_view.tabs.count()
print('admin tabs:', [w.admin_view.tabs.tabText(i) for i in range(w.admin_view.tabs.count())])
"
```
Expected: `admin tabs: ['Coefficients', 'Répartition']`

- [ ] **Step 8: Commit**

```bash
git add src/devis_batiment/storage.py src/devis_batiment/config.py src/devis_batiment/services/__init__.py src/devis_batiment/ui/admin_view.py tests/test_storage.py tests/test_services.py
git commit -m "refactor: remove disconnected pricing-profile system

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3 : `QuoteService.load_quote` (réouverture de devis, couche service)

**Files:**
- Modify: `src/devis_batiment/services/__init__.py`
- Test: `tests/test_services.py`

**Interfaces:**
- Produces: `QuoteService.load_quote(quote_id: int) -> tuple[QuoteInput, QuoteEstimate]` — reconstruit input+estimate depuis le payload persisté, sans réinsérer.
- Consumes: `Database.fetch_quote_payload(quote_id)` (existant).

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter dans `tests/test_services.py` :

```python
def test_quote_service_loads_persisted_quote(tmp_path: Path):
    database = Database(tmp_path / "load.db")
    database.initialize()
    service = QuoteService(database)
    quote_input = QuoteInput(
        client_name="Mme Ranaivo",
        client_contact="0321111111",
        project_name="Villa",
        project_type="Maison",
        location="Toamasina",
        surface_m2=95,
        length_m=0.0,
        width_m=0.0,
        height_m=0.0,
        thickness_m=0.0,
        floors=1,
        structure_type="Béton armé",
        roof_type="Tôle",
        room_count=4,
        finish_level="Économique",
        complexity="Simple",
    )
    estimate = QuoteEstimate(
        total_amount=56_000_000.0,
        applied_multipliers={"Marge de sécurité": 1.0},
        breakdown={"Matériaux": 56_000_000.0},
        materials=[MaterialLine("Ciment", "sacs", 100, 45_000, 4_500_000)],
        volume_m3=11.4,
    )
    saved_id = service.save_quote(quote_input, estimate)

    loaded_input, loaded_estimate = service.load_quote(saved_id)

    assert loaded_input == quote_input
    assert loaded_estimate.total_amount == 56_000_000.0
    assert loaded_estimate.materials[0].name == "Ciment"
    assert loaded_estimate.volume_m3 == 11.4
```

- [ ] **Step 2: Lancer le test pour vérifier l'échec**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_services.py::test_quote_service_loads_persisted_quote -v`
Expected: FAIL avec `AttributeError: 'QuoteService' object has no attribute 'load_quote'`.

- [ ] **Step 3: Implémenter `load_quote` et refactorer `duplicate_quote`**

Dans `src/devis_batiment/services/__init__.py`, classe `QuoteService`, ajouter :

```python
    def load_quote(self, quote_id: int) -> tuple[QuoteInput, QuoteEstimate]:
        payload = self.database.fetch_quote_payload(quote_id)
        quote_input = QuoteInput(**payload["input"])
        estimate = QuoteEstimate(
            total_amount=payload["estimate"]["total_amount"],
            applied_multipliers=payload["estimate"]["applied_multipliers"],
            breakdown=payload["estimate"]["breakdown"],
            materials=[
                MaterialLine(**line)
                for line in payload["estimate"].get("materials", [])
            ],
            volume_m3=float(payload["estimate"].get("volume_m3", 0.0)),
        )
        return quote_input, estimate
```

Remplacer le corps de `duplicate_quote` pour réutiliser `load_quote` :

```python
    def duplicate_quote(self, quote_id: int) -> int:
        quote_input, estimate = self.load_quote(quote_id)
        return self.database.insert_quote(quote_input, estimate)
```

- [ ] **Step 4: Lancer les tests pour vérifier le succès**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_services.py -v`
Expected: PASS (nouveau test + `test_quote_service_can_search_and_duplicate_quotes` toujours vert).

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/services/__init__.py tests/test_services.py
git commit -m "feat(services): add load_quote and reuse it in duplicate_quote

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4 : Formatage devise partagé

**Files:**
- Create: `src/devis_batiment/ui/formatting.py`
- Test: `tests/test_ui_smoke.py`

**Interfaces:**
- Produces: `format_amount(amount: float, currency: str = "Ar") -> str` — ex. `format_amount(1234567) == "1 234 567 Ar"`, `format_amount(1000, "MGA") == "1 000 MGA"`.

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter dans `tests/test_ui_smoke.py` :

```python
def test_format_amount_uses_currency_and_space_separator():
    from devis_batiment.ui.formatting import format_amount

    assert format_amount(1_234_567) == "1 234 567 Ar"
    assert format_amount(1000, "MGA") == "1 000 MGA"
    assert format_amount(0) == "0 Ar"
```

- [ ] **Step 2: Lancer le test pour vérifier l'échec**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_ui_smoke.py::test_format_amount_uses_currency_and_space_separator -v`
Expected: FAIL avec `ModuleNotFoundError: No module named 'devis_batiment.ui.formatting'`.

- [ ] **Step 3: Créer le helper**

Créer `src/devis_batiment/ui/formatting.py` :

```python
from __future__ import annotations


def format_amount(amount: float, currency: str = "Ar") -> str:
    return f"{amount:,.0f} {currency}".replace(",", " ")
```

- [ ] **Step 4: Lancer le test pour vérifier le succès**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_ui_smoke.py::test_format_amount_uses_currency_and_space_separator -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/devis_batiment/ui/formatting.py tests/test_ui_smoke.py
git commit -m "feat(ui): add shared currency formatting helper

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5 : Brancher la devise dans les vues

**Files:**
- Modify: `src/devis_batiment/ui/quote_result.py`
- Modify: `src/devis_batiment/ui/history_view.py`
- Modify: `src/devis_batiment/ui/dashboard_view.py`
- Modify: `src/devis_batiment/ui/main_window.py`

**Interfaces:**
- Consumes: `format_amount` (Task 4), `SettingsService.get("currency")`.
- Produces: chaque vue expose `set_currency(currency: str)` et l'utilise pour son affichage ; `MainWindow` propage la devise sur les changements de page.

- [ ] **Step 1: quote_result — devise paramétrable**

Dans `src/devis_batiment/ui/quote_result.py` :
- Remplacer le helper local `_fmt_mga` par un import :
  `from devis_batiment.ui.formatting import format_amount`.
- Ajouter un attribut `self._currency = "Ar"` dans `__init__` et une méthode :

```python
    def set_currency(self, currency: str) -> None:
        self._currency = currency or "Ar"
```

- Dans `show_result`, remplacer chaque `_fmt_mga(x)` par
  `format_amount(x, self._currency)`.

- [ ] **Step 2: history_view — devise paramétrable**

Dans `src/devis_batiment/ui/history_view.py` :
- Remplacer `_fmt_mga` par `from devis_batiment.ui.formatting import format_amount`.
- Ajouter `self._currency = "Ar"` dans `__init__` et :

```python
    def set_currency(self, currency: str) -> None:
        self._currency = currency or "Ar"
        self.refresh()
```

- Dans `_populate`, utiliser `format_amount(float(row["total_amount"]), self._currency)`.

- [ ] **Step 3: dashboard_view — devise paramétrable**

Dans `src/devis_batiment/ui/dashboard_view.py` :
- Remplacer `_fmt_amount` par `from devis_batiment.ui.formatting import format_amount`.
- Ajouter `self._currency = "Ar"` dans `__init__` et :

```python
    def set_currency(self, currency: str) -> None:
        self._currency = currency or "Ar"
```

- Dans `refresh`, utiliser `format_amount(total_revenue, self._currency)` et
  `format_amount(float(row["total_amount"]), self._currency)`.

- [ ] **Step 4: main_window — propager la devise**

Dans `src/devis_batiment/ui/main_window.py`, méthode `_on_page_changed`,
appliquer la devise courante avant chaque `refresh` des vues concernées :

```python
    def _on_page_changed(self, index: int) -> None:
        currency = self.settings_service.get("currency") or "Ar"
        if index == 0:
            self.dashboard_view.set_currency(currency)
            self.dashboard_view.refresh()
        elif index == 1:
            self.clients_view.refresh()
        elif index == 2:
            self.projects_view.refresh()
        elif index == 3:
            self.history_view.set_currency(currency)
            self.history_view.refresh()
        elif index == 4:
            self.materials_view.refresh()
        elif index == 5:
            self.admin_view.refresh()
        elif index == 6:
            self.settings_view.load()
```

Dans `_on_quote_requested`, avant `self.quote_result.show_result(...)`, ajouter :

```python
        self.quote_result.set_currency(self.settings_service.get("currency") or "Ar")
```

(`history_view.set_currency` appelle déjà `refresh()`, donc ne pas doubler le
`refresh` : dans la branche `index == 3`, retirer l'appel `self.history_view.refresh()`
si `set_currency` le fait — pour rester simple, garder uniquement
`self.history_view.set_currency(currency)`.)

- [ ] **Step 5: Lancer toute la suite**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -v`
Expected: PASS

- [ ] **Step 6: Vérifier à la main que la devise se propage**

Run:
```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -c "
from PySide6.QtWidgets import QApplication
app = QApplication([])
from devis_batiment.app import create_main_window
w = create_main_window()
w.settings_service.set('currency', 'MGA')
w.pages.setCurrentIndex(0)
print(w.dashboard_view.revenue_label.text())
"
```
Expected: le texte du label contient « MGA ».

- [ ] **Step 7: Commit**

```bash
git add src/devis_batiment/ui/quote_result.py src/devis_batiment/ui/history_view.py src/devis_batiment/ui/dashboard_view.py src/devis_batiment/ui/main_window.py
git commit -m "feat(ui): apply configured currency across result, history and dashboard

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6 : Réouverture d'un devis depuis l'historique (câblage UI)

**Files:**
- Modify: `src/devis_batiment/ui/history_view.py`
- Modify: `src/devis_batiment/ui/main_window.py`
- Test: `tests/test_ui_smoke.py`

**Interfaces:**
- Consumes: `QuoteService.load_quote` (Task 3), signal `HistoryView.open_quote_requested(int)`.
- Produces: double-clic sur une ligne d'historique → émet `open_quote_requested(quote_id)` ; `MainWindow` affiche le résultat persisté.

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter dans `tests/test_ui_smoke.py` (suivre le style des tests UI existants qui
créent `MainWindow(Database(Path(":memory:")))`) :

```python
def test_open_quote_from_history_shows_result(qtbot):
    from pathlib import Path
    from devis_batiment.models import MaterialLine, QuoteEstimate, QuoteInput
    from devis_batiment.storage import Database
    from devis_batiment.ui.main_window import MainWindow

    window = MainWindow(Database(Path(":memory:")))
    qtbot.addWidget(window)

    quote_input = QuoteInput(
        client_name="Client Test", client_contact="", project_name="P",
        project_type="Maison", location="Antananarivo", surface_m2=100,
        length_m=0.0, width_m=0.0, height_m=0.0, thickness_m=0.0, floors=1,
        structure_type="Béton armé", roof_type="Tôle", room_count=3,
        finish_level="Standard", complexity="Simple",
    )
    estimate = QuoteEstimate(
        total_amount=12_000_000.0, applied_multipliers={"Marge de sécurité": 1.0},
        breakdown={"Matériaux": 12_000_000.0},
        materials=[MaterialLine("Ciment", "sacs", 10, 45_000, 450_000)],
        volume_m3=5.0,
    )
    saved_id = window.quote_service.save_quote(quote_input, estimate)

    window._on_open_quote_requested(saved_id)

    assert window.pages.currentIndex() == 3
    assert window.devis_tabs.currentIndex() == 1
    assert "12 000 000" in window.quote_result._total_label.text()
```

- [ ] **Step 2: Lancer le test pour vérifier l'échec**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_ui_smoke.py::test_open_quote_from_history_shows_result -v`
Expected: FAIL avec `AttributeError: 'MainWindow' object has no attribute '_on_open_quote_requested'`.

- [ ] **Step 3: Émettre le signal au double-clic (history_view)**

Dans `src/devis_batiment/ui/history_view.py`, à la fin de `__init__` (après les
autres `connect`), ajouter :

```python
        self.quote_table.cellDoubleClicked.connect(self._on_row_double_clicked)
```

et la méthode :

```python
    def _on_row_double_clicked(self, row: int, _column: int) -> None:
        id_item = self.quote_table.item(row, 0)
        if id_item is None:
            return
        quote_id = int(id_item.data(Qt.ItemDataRole.UserRole))
        self.open_quote_requested.emit(quote_id)
```

- [ ] **Step 4: Câbler la réouverture (main_window)**

Dans `src/devis_batiment/ui/main_window.py`, après la connexion existante
`self.quote_form.quote_requested.connect(...)`, ajouter :

```python
        self.history_view.open_quote_requested.connect(self._on_open_quote_requested)
```

et la méthode :

```python
    def _on_open_quote_requested(self, quote_id: int) -> None:
        try:
            quote_input, estimate = self.quote_service.load_quote(quote_id)
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le devis :\n{exc}")
            return
        self.quote_result.set_currency(self.settings_service.get("currency") or "Ar")
        self.quote_result.show_result(quote_id, quote_input, estimate)
        self.devis_tabs.setCurrentIndex(1)
        self.pages.setCurrentIndex(3)
```

- [ ] **Step 5: Lancer le test pour vérifier le succès**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_ui_smoke.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/devis_batiment/ui/history_view.py src/devis_batiment/ui/main_window.py tests/test_ui_smoke.py
git commit -m "feat(ui): reopen a stored quote from history on double-click

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 7 : Export PDF branché

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/devis_batiment/ui/quote_result.py`
- Modify: `src/devis_batiment/ui/main_window.py`
- Test: `tests/test_pdf.py` (créer)

**Interfaces:**
- Consumes: `export_quote_pdf` ([utils/pdf.py](../../../src/devis_batiment/utils/pdf.py)), `SettingsService.get_all()`.
- Produces: `QuoteResultWidget` mémorise le dernier `(quote_id, quote_input, estimate)` ; bouton « Exporter en PDF » actif seulement quand un résultat est affiché ; méthode `set_settings_service(service)`.

- [ ] **Step 1: Déclarer reportlab**

Dans `pyproject.toml`, section `dependencies`, ajouter la ligne reportlab :

```toml
dependencies = [
  "PySide6_Essentials>=6.8,<7.0",
  "reportlab>=4.0,<5.0",
]
```

- [ ] **Step 2: Écrire le test PDF qui échoue**

Créer `tests/test_pdf.py` :

```python
from pathlib import Path

from devis_batiment.models import MaterialLine, QuoteEstimate, QuoteInput
from devis_batiment.utils.pdf import export_quote_pdf


def test_export_quote_pdf_writes_non_empty_file(tmp_path: Path):
    quote_input = QuoteInput(
        client_name="Client Test", client_contact="0340000000",
        project_name="Maison", project_type="Maison", location="Antananarivo",
        surface_m2=100, length_m=0.0, width_m=0.0, height_m=0.0, thickness_m=0.0,
        floors=1, structure_type="Béton armé", roof_type="Tôle", room_count=3,
        finish_level="Standard", complexity="Simple",
    )
    estimate = QuoteEstimate(
        total_amount=12_000_000.0, applied_multipliers={"Marge de sécurité": 1.0},
        breakdown={"Matériaux": 12_000_000.0},
        materials=[MaterialLine("Ciment", "sacs 50kg", 10, 45_000, 450_000)],
        volume_m3=5.0,
    )
    company_info = {"company_name": "Jeannot Devis Bâtiment", "currency": "Ar"}
    output = tmp_path / "devis_1.pdf"

    result = export_quote_pdf(output, company_info, 1, quote_input, estimate)

    assert result == output
    assert output.exists()
    assert output.stat().st_size > 0
```

- [ ] **Step 3: Lancer le test pour vérifier le succès (ou l'échec d'import)**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_pdf.py -v`
Expected: PASS si reportlab est installé dans le venv (il l'est déjà). Si
`ModuleNotFoundError`, lancer `.venv/bin/pip install -e ".[dev]"` puis relancer.

- [ ] **Step 4: Mémoriser le dernier résultat + bouton d'export (quote_result)**

Dans `src/devis_batiment/ui/quote_result.py` :
- Importer `QPushButton`, `QFileDialog`, `QMessageBox` depuis `PySide6.QtWidgets`
  et `from devis_batiment.utils.pdf import export_quote_pdf`.
- Dans `__init__`, ajouter les attributs :

```python
        self._settings_service = None
        self._last_quote_id: int | None = None
        self._last_input = None
        self._last_estimate = None
```

- Ajouter un bouton d'export (par ex. dans le `total_frame` ou juste sous lui) :

```python
        self._export_button = QPushButton("Exporter en PDF")
        self._export_button.setEnabled(False)
        self._export_button.clicked.connect(self._on_export_pdf)
        total_layout.addWidget(self._export_button)
```

- Ajouter le setter du service :

```python
    def set_settings_service(self, settings_service) -> None:
        self._settings_service = settings_service
```

- Dans `show_result`, au début, mémoriser et activer le bouton :

```python
        self._last_quote_id = quote_id
        self._last_input = quote_input
        self._last_estimate = estimate
        self._export_button.setEnabled(True)
```

- Ajouter le handler d'export :

```python
    def _on_export_pdf(self) -> None:
        if self._last_estimate is None or self._last_input is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter le devis en PDF",
            f"devis_{self._last_quote_id}.pdf", "PDF (*.pdf)",
        )
        if not path:
            return
        company_info = (
            self._settings_service.get_all() if self._settings_service else {}
        )
        try:
            from pathlib import Path
            export_quote_pdf(
                Path(path), company_info, self._last_quote_id or 0,
                self._last_input, self._last_estimate,
            )
            QMessageBox.information(self, "Export PDF", f"Devis exporté :\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", f"Échec de l'export PDF :\n{exc}")
```

- Dans `clear`, remettre `self._export_button.setEnabled(False)`.

- [ ] **Step 5: Injecter le settings_service (main_window)**

Dans `src/devis_batiment/ui/main_window.py`, `_build_ui`, après la création de
`self.quote_result = QuoteResultWidget()`, ajouter :

```python
        self.quote_result.set_settings_service(self.settings_service)
```

- [ ] **Step 6: Lancer toute la suite + smoke UI export**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -v`
Expected: PASS

Run (smoke bouton) :
```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -c "
from PySide6.QtWidgets import QApplication
app = QApplication([])
from devis_batiment.app import create_main_window
w = create_main_window()
assert w.quote_result._export_button.isEnabled() is False
print('export button initial state OK')
"
```
Expected: `export button initial state OK`

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/devis_batiment/ui/quote_result.py src/devis_batiment/ui/main_window.py tests/test_pdf.py
git commit -m "feat(ui): wire PDF export from the result screen

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 8 : Nettoyage & cohérence de nommage

**Files:**
- Modify: `src/devis_batiment/ui/main_window.py`
- Modify: `src/devis_batiment/app.py`
- Modify: `src/devis_batiment/services/__init__.py`
- Modify: `src/devis_batiment/utils/pdf.py`
- Modify: `src/devis_batiment/ui/admin_view.py`
- Delete: `devis_batiment.db`
- Test: `tests/test_smoke.py`

**Interfaces:**
- Produces: nom d'app « Jeannot Devis Bâtiment » cohérent ; `build_app_metadata()["app_name"] == "Jeannot Devis Bâtiment"`.

- [ ] **Step 1: Mettre à jour les tests smoke**

Dans `tests/test_smoke.py` :
- Ligne 12 : `assert metadata["app_name"] == "Jeannot Devis Batiment"` →
  `assert metadata["app_name"] == "Jeannot Devis Bâtiment"` (ajout de l'accent).
- Ligne 22 : `assert window.windowTitle() == "SmartBTP Devis Desktop"` →
  `assert window.windowTitle() == "Jeannot Devis Bâtiment"`.
- Laisser inchangées les assertions `database_name == "devis_batiment.db"` et
  `currency == "MGA"` (hors périmètre).

- [ ] **Step 2: Lancer le test pour vérifier l'échec**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_smoke.py -v`
Expected: FAIL sur les deux assertions modifiées (l'app renvoie encore
« Jeannot Devis Batiment » sans accent et le titre « SmartBTP Devis Desktop »).

- [ ] **Step 3: Uniformiser le nom d'application**

- `src/devis_batiment/app.py` : `build_app_metadata` → `"app_name": "Jeannot Devis Bâtiment"`.
- `src/devis_batiment/ui/main_window.py` : `self.setWindowTitle("Jeannot Devis Bâtiment")`
  et le `QLabel("SmartBTP Devis Desktop")` d'en-tête → `QLabel("Jeannot Devis Bâtiment")`.
- `src/devis_batiment/services/__init__.py` :
  `SETTING_DEFAULTS["company_name"] = "Jeannot Devis Bâtiment"`.
- `src/devis_batiment/utils/pdf.py` : remplacer les deux occurrences de défaut
  `"SmartBTP Devis Desktop"` par `"Jeannot Devis Bâtiment"`.

- [ ] **Step 4: Nettoyer admin_view.py**

Dans `src/devis_batiment/ui/admin_view.py` :
- Remonter l'import `from devis_batiment.services import AdminService` en haut du
  fichier, avec les autres imports (ligne ~39 actuellement, après du code).
- Dans `_AdjustmentDialog._on_accept`, supprimer la ligne no-op
  `self.category.setCurrentIndex(self.category.currentIndex())`.
- Supprimer la classe morte imbriquée `_CategoryCombo` (jamais instanciée).

- [ ] **Step 5: Supprimer la base obsolète**

```bash
git rm --ignore-unmatch devis_batiment.db 2>/dev/null; rm -f devis_batiment.db
```
(La base est ignorée par `.gitignore` et non suivie : `rm -f` suffit.)

- [ ] **Step 6: Lancer toute la suite + smoke**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -v`
Expected: PASS

Run:
```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -c "
from PySide6.QtWidgets import QApplication
app = QApplication([])
from devis_batiment.app import create_main_window
w = create_main_window()
print('title:', w.windowTitle())
"
```
Expected: `title: Jeannot Devis Bâtiment`

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: unify app name and remove dead code / stale db

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 9 : README à jour

**Files:**
- Modify: `README.md`

**Interfaces:** documentation seule.

- [ ] **Step 1: Corriger structure, formule, PDF, note FK**

Dans `README.md` :
- Section « Structure du projet » : remplacer `calculator.py`/`services.py` par
  `services/` (package : `__init__.py`, `calcul_btp.py`), `utils/pdf.py`, et
  lister les vues réelles (`dashboard_view`, `clients_view`, `projects_view`,
  `materials_view`, en plus des existantes).
- Section « Architecture » / « Formule de calcul » : remplacer
  `surface × prix_base × ∏ coefficients` par le calcul réel :
  `volume estimé → quantités de matériaux → Σ (quantité × prix) × ∏ coefficients × (1 + marge)`.
  Retirer la mention `pricing_profiles` de la liste des tables (4 tables de
  référence restantes : `adjustment_rules`, `breakdown_rules`, `quotes`+`quote_lines`,
  `clients`/`projects`/`materials`/`settings`).
- Ajouter une phrase : export PDF disponible depuis l'écran de résultat.
- Ajouter une note : l'intégrité référentielle (cascades) s'applique aux bases
  créées avec cette version ; la ligne d'en-tête `# JEANNOT` en double en bas du
  fichier peut être supprimée.

- [ ] **Step 2: Vérifier qu'aucune référence obsolète ne subsiste**

Run: `grep -nE "calculator\.py|services\.py|prix_base|pricing_profiles|SmartBTP" README.md || echo "clean"`
Expected: `clean`

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README to match current architecture

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 10 : Vérification finale

**Files:** aucun (validation).

- [ ] **Step 1: Suite complète**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -v`
Expected: 100 % PASS.

- [ ] **Step 2: Démarrage complet de l'app (offscreen)**

Run:
```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -c "
from PySide6.QtWidgets import QApplication
app = QApplication([])
from devis_batiment.app import create_main_window
w = create_main_window()
w.show()
for i in range(w.pages.count()):
    w.pages.setCurrentIndex(i)
print('pages:', w.pages.count(), '| admin tabs:', w.admin_view.tabs.count(), '| title:', w.windowTitle())
"
```
Expected: `pages: 7 | admin tabs: 2 | title: Jeannot Devis Bâtiment` sans exception.

- [ ] **Step 3: Rapport**

Confirmer : profils de prix supprimés, export PDF fonctionnel, réouverture de
devis OK, devise propagée, cascades FK actives, README cohérent, suite verte.
```
```

## Notes d'exécution

- Ordre imposé par les dépendances : Task 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10.
  (Task 6 dépend de 3 ; Task 5 dépend de 4 ; Task 7 est indépendant de 5/6 mais
  placé après pour réutiliser `set_currency` déjà en place.)
- Après chaque tâche à effet fonctionnel, la suite doit rester verte.
