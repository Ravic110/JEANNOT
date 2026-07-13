from __future__ import annotations

from pathlib import Path


def default_database_path() -> Path:
    database_dir = Path.cwd() / "database"
    database_dir.mkdir(exist_ok=True)
    return database_dir / "db.sqlite"


# ---------------------------------------------------------------------------
# Listes de référence (valeurs proposées dans le formulaire)
# ---------------------------------------------------------------------------

LOCATIONS = [
    "Antananarivo",
    "Fianarantsoa",
    "Toamasina",
    "Mahajanga",
    "Toliara",
    "Antsiranana",
    "Autre",
]

STRUCTURE_TYPES = [
    "Maçonnerie",
    "Béton armé",
    "Charpente métallique",
    "Mixte",
]

ROOF_TYPES = [
    "Tuile",
    "Tôle",
    "Terrasse béton",
    "Chaume",
]

FINISH_LEVELS = [
    "Économique",
    "Standard",
    "Haut de gamme",
]

COMPLEXITY_LEVELS = [
    "Simple",
    "Moyenne",
    "Complexe",
]

PROJECT_TYPES = [
    "Maison",
    "Mur",
    "Dalle béton",
    "Route",
    "Fondation",
    "Poteau",
    "Autre",
]

FLOORS_ADJUSTMENT_KEYS = ["1", "2", "3", "4", "5+"]

DEFAULT_MATERIALS: list[dict[str, object]] = [
    {"name": "Ciment", "unit": "sacs 50kg", "unit_price": 45_000.0},
    {"name": "Sable", "unit": "m³", "unit_price": 180_000.0},
    {"name": "Gravier", "unit": "m³", "unit_price": 190_000.0},
    {"name": "Fer", "unit": "kg", "unit_price": 4_000.0},
    {"name": "Main d'œuvre", "unit": "jour", "unit_price": 220_000.0},
]

# ---------------------------------------------------------------------------
# Données initiales par défaut (prix et coefficients de référence Madagascar)
# Ces valeurs sont insérées au premier démarrage si la base est vide.
# ---------------------------------------------------------------------------

DEFAULT_ADJUSTMENT_RULES: list[dict[str, object]] = [
    # Localisation
    {"category": "location", "rule_key": "Antananarivo", "multiplier": 1.10},
    {"category": "location", "rule_key": "Fianarantsoa", "multiplier": 0.95},
    {"category": "location", "rule_key": "Toamasina", "multiplier": 1.00},
    {"category": "location", "rule_key": "Mahajanga", "multiplier": 1.05},
    {"category": "location", "rule_key": "Toliara", "multiplier": 0.90},
    {"category": "location", "rule_key": "Antsiranana", "multiplier": 1.05},
    {"category": "location", "rule_key": "Autre", "multiplier": 1.00},
    # Type de structure
    {"category": "structure_type", "rule_key": "Maçonnerie", "multiplier": 1.00},
    {"category": "structure_type", "rule_key": "Béton armé", "multiplier": 1.15},
    {"category": "structure_type", "rule_key": "Charpente métallique", "multiplier": 1.10},
    {"category": "structure_type", "rule_key": "Mixte", "multiplier": 1.08},
    # Type de toiture
    {"category": "roof_type", "rule_key": "Tuile", "multiplier": 1.05},
    {"category": "roof_type", "rule_key": "Tôle", "multiplier": 0.95},
    {"category": "roof_type", "rule_key": "Terrasse béton", "multiplier": 1.10},
    {"category": "roof_type", "rule_key": "Chaume", "multiplier": 0.85},
    # Complexité
    {"category": "complexity", "rule_key": "Simple", "multiplier": 0.95},
    {"category": "complexity", "rule_key": "Moyenne", "multiplier": 1.00},
    {"category": "complexity", "rule_key": "Complexe", "multiplier": 1.15},
    # Nombre d'étages
    {"category": "floors", "rule_key": "1", "multiplier": 1.00},
    {"category": "floors", "rule_key": "2", "multiplier": 1.08},
    {"category": "floors", "rule_key": "3", "multiplier": 1.14},
    {"category": "floors", "rule_key": "4", "multiplier": 1.20},
    {"category": "floors", "rule_key": "5+", "multiplier": 1.28},
]

DEFAULT_BREAKDOWN_RULES: list[dict[str, object]] = [
    {"lot_name": "Études et préparation", "percentage": 0.04},
    {"lot_name": "Terrassement et fondations", "percentage": 0.12},
    {"lot_name": "Structure et élévation", "percentage": 0.28},
    {"lot_name": "Charpente et toiture", "percentage": 0.10},
    {"lot_name": "Menuiseries", "percentage": 0.08},
    {"lot_name": "Électricité et plomberie", "percentage": 0.14},
    {"lot_name": "Revêtements et finitions", "percentage": 0.16},
    {"lot_name": "Divers et imprévus", "percentage": 0.08},
]
