from __future__ import annotations

from pathlib import Path


def default_database_path() -> Path:
    return Path.cwd() / "devis_batiment.db"
