# Jeannot Devis Bâtiment

Application desktop interne pour produire des devis approximatifs de construction à Madagascar.

## Fonctionnalités

- **Nouveau devis** — formulaire complet (client, surface, étages, structure, toiture, finition, complexité...)
- **Résultat** — montant total estimé en Ariary, coefficients appliqués, ventilation par grands postes
- **Historique** — liste, recherche et duplication des devis précédents
- **Administration** — gestion des profils de prix, coefficients d'ajustement et répartition par lots
- **Paramètres** — informations de l'entreprise, devise, marge de sécurité, validité des devis

## Prérequis

- Python 3.12+
- PySide6

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -e ".[dev]"
```

## Lancement

```bash
python main.py
```

Ou via le module :

```bash
python -m devis_batiment.app
```

La base de données `devis_batiment.db` est créée automatiquement dans le répertoire courant au premier lancement. Les données de référence (prix, coefficients, répartition) sont insérées par défaut si la base est vide.

## Tests

```bash
QT_QPA_PLATFORM=offscreen pytest -v
```

## Structure du projet

```
src/devis_batiment/
├── app.py            # Point d'entrée et bootstrap
├── calculator.py     # Moteur de calcul estimatif
├── config.py         # Listes de référence et données initiales
├── models.py         # Modèles de données (QuoteInput, QuoteEstimate)
├── services.py       # Logique métier (Quote, Admin, Settings)
├── storage.py        # Couche SQLite
└── ui/
    ├── main_window.py   # Fenêtre principale
    ├── quote_form.py    # Formulaire de saisie
    ├── quote_result.py  # Affichage du résultat
    ├── history_view.py  # Historique des devis
    ├── admin_view.py    # Administration des paramètres de calcul
    └── settings_view.py # Paramètres de l'application
```

## Architecture

```
models.py       ← Dataclasses (QuoteInput, QuoteEstimate)
storage.py      ← SQLite — 5 tables : pricing_profiles, adjustment_rules,
                             breakdown_rules, quotes, settings
calculator.py   ← Calcul : surface × prix_base × coefficients
services.py     ← QuoteService, AdminService, SettingsService, QuoteWorkflow
ui/             ← Interface PySide6 (Qt)
```

### Formule de calcul

```
Montant estimé = surface (m²) × prix_de_base (Ar/m²) × ∏ coefficients
Montant par poste = montant estimé × pourcentage_du_poste
```
# JEANNOT
