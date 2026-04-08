from pathlib import Path

from PySide6.QtWidgets import QApplication

from devis_batiment.app import build_app_metadata
from devis_batiment.app import create_main_window


def test_build_app_metadata_returns_expected_defaults():
    metadata = build_app_metadata()

    assert metadata["app_name"] == "Jeannot Devis Batiment"
    assert metadata["database_name"] == "devis_batiment.db"
    assert metadata["currency"] == "MGA"


def test_create_main_window_uses_default_database_name(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = QApplication.instance() or QApplication([])

    window = create_main_window()

    assert window.database.path.name == "devis_batiment.db"
    assert window.windowTitle() == "Jeannot Devis Bâtiment"
