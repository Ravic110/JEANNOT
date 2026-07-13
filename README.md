# Jeannot Devis Bâtiment

Application desktop interne pour produire des devis approximatifs de construction à Madagascar.

## Fonctionnalités

- **Nouveau devis** — formulaire complet (client, surface, étages, structure, toiture, finition, complexité...)
- **Résultat** — montant total estimé en Ariary, coefficients appliqués, ventilation par grands postes ; export du devis en PDF disponible directement depuis cet écran
- **Historique** — liste, recherche et duplication des devis précédents
- **Administration** — gestion des matériaux et de leur prix, coefficients d'ajustement et répartition par lots
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
├── app.py              # Point d'entrée et bootstrap
├── config.py           # Listes de référence et données initiales
├── models.py           # Modèles de données (QuoteInput, QuoteEstimate, MaterialLine)
├── storage.py          # Couche SQLite
├── services/
│   ├── __init__.py    # Logique métier (QuoteService, AdminService, ClientService,
│   │                  #   ProjectService, SettingsService, QuoteWorkflow)
│   └── calcul_btp.py  # Moteur de calcul estimatif (BtpQuoteCalculator)
├── utils/
│   └── pdf.py         # Export du devis en PDF
└── ui/
    ├── main_window.py     # Fenêtre principale
    ├── dashboard_view.py  # Tableau de bord
    ├── quote_form.py      # Formulaire de saisie
    ├── quote_result.py    # Affichage du résultat (+ export PDF)
    ├── history_view.py    # Historique des devis
    ├── clients_view.py    # Gestion des clients
    ├── projects_view.py   # Gestion des projets
    ├── materials_view.py  # Gestion des matériaux et de leur prix
    ├── admin_view.py      # Administration des coefficients et de la répartition
    └── settings_view.py   # Paramètres de l'application
```

## Architecture

```
models.py               ← Dataclasses (QuoteInput, QuoteEstimate, MaterialLine)
storage.py              ← SQLite — tables adjustment_rules, breakdown_rules,
                            quotes/quote_lines, clients/projects, materials,
                            settings
services/calcul_btp.py ← BtpQuoteCalculator : moteur de calcul
services/__init__.py   ← QuoteService, AdminService, ClientService,
                            ProjectService, SettingsService, QuoteWorkflow
utils/pdf.py            ← Export PDF du devis
ui/                     ← Interface PySide6 (Qt)
```

### Formule de calcul

Le calcul ne se base plus sur un prix au m² : il estime un volume à partir
des dimensions et du type de projet, puis en déduit des quantités de
matériaux.

```
1. volume_m3        = f(type_de_projet, longueur, largeur, hauteur,
                         épaisseur, surface)
2. quantité(matériau) = f(volume_m3)   # ciment, sable, gravier, fer, main d'œuvre
3. montant_matériaux = Σ (quantité × prix_unitaire)
4. montant_ajusté    = montant_matériaux × ∏ coefficients
                         (localisation, structure, toiture, complexité, étages)
5. montant_final     = montant_ajusté × (1 + marge_de_sécurité)
6. montant_par_poste = montant_final × pourcentage_du_poste (breakdown_rules)
```

## Notes

- L'export PDF d'un devis est disponible directement depuis l'écran de
  résultat (bouton « Exporter en PDF »).
- L'intégrité référentielle par clés étrangères (cascades `ON DELETE CASCADE`,
  ex. suppression d'un client entraînant celle de ses projets) est activée
  (`PRAGMA foreign_keys = ON`) et s'applique aux bases de données créées avec
  cette version de l'application.
