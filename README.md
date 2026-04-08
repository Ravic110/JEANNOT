# Jeannot Devis Batiment

Application desktop pour produire des devis approximatifs de construction.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Lancer l'application

```bash
python -m devis_batiment.app
```

## Lancer les tests

```bash
QT_QPA_PLATFORM=offscreen pytest -v
```
