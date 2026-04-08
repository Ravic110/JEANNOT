from __future__ import annotations

from pathlib import Path


def default_database_path() -> Path:
    return Path.cwd() / "devis_batiment.db"


# ---------------------------------------------------------------------------
# Listes de référence (valeurs proposées dans le formulaire)
# ---------------------------------------------------------------------------

BUILDING_TYPES = [
    "Villa",
    "Immeuble résidentiel",
    "Local commercial",
    "Entrepôt",
    "Bureau",
    "École / Formation",
    "Autre",
]

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

FLOORS_ADJUSTMENT_KEYS = ["1", "2", "3", "4", "5+"]

# ---------------------------------------------------------------------------
# Données initiales par défaut (prix et coefficients de référence Madagascar)
# Ces valeurs sont insérées au premier démarrage si la base est vide.
# ---------------------------------------------------------------------------

DEFAULT_PRICING_PROFILES: list[dict[str, object]] = [
    # (type de bâtiment, finition, prix de base en MGA/m²)
    {"building_type": "Villa", "finish_level": "Économique", "base_price_per_m2": 800_000.0},
    {"building_type": "Villa", "finish_level": "Standard", "base_price_per_m2": 1_200_000.0},
    {"building_type": "Villa", "finish_level": "Haut de gamme", "base_price_per_m2": 1_800_000.0},
    {"building_type": "Immeuble résidentiel", "finish_level": "Économique", "base_price_per_m2": 700_000.0},
    {"building_type": "Immeuble résidentiel", "finish_level": "Standard", "base_price_per_m2": 1_000_000.0},
    {"building_type": "Immeuble résidentiel", "finish_level": "Haut de gamme", "base_price_per_m2": 1_500_000.0},
    {"building_type": "Local commercial", "finish_level": "Économique", "base_price_per_m2": 650_000.0},
    {"building_type": "Local commercial", "finish_level": "Standard", "base_price_per_m2": 950_000.0},
    {"building_type": "Local commercial", "finish_level": "Haut de gamme", "base_price_per_m2": 1_400_000.0},
    {"building_type": "Entrepôt", "finish_level": "Économique", "base_price_per_m2": 450_000.0},
    {"building_type": "Entrepôt", "finish_level": "Standard", "base_price_per_m2": 650_000.0},
    {"building_type": "Entrepôt", "finish_level": "Haut de gamme", "base_price_per_m2": 900_000.0},
    {"building_type": "Bureau", "finish_level": "Économique", "base_price_per_m2": 700_000.0},
    {"building_type": "Bureau", "finish_level": "Standard", "base_price_per_m2": 1_050_000.0},
    {"building_type": "Bureau", "finish_level": "Haut de gamme", "base_price_per_m2": 1_600_000.0},
    {"building_type": "École / Formation", "finish_level": "Économique", "base_price_per_m2": 600_000.0},
    {"building_type": "École / Formation", "finish_level": "Standard", "base_price_per_m2": 850_000.0},
    {"building_type": "École / Formation", "finish_level": "Haut de gamme", "base_price_per_m2": 1_200_000.0},
    {"building_type": "Autre", "finish_level": "Économique", "base_price_per_m2": 700_000.0},
    {"building_type": "Autre", "finish_level": "Standard", "base_price_per_m2": 1_000_000.0},
    {"building_type": "Autre", "finish_level": "Haut de gamme", "base_price_per_m2": 1_500_000.0},
]

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
