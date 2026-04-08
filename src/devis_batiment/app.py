from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication

from devis_batiment.config import default_database_path
from devis_batiment.storage import Database
from devis_batiment.ui import theme
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
    theme.apply(app)
    window = create_main_window()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
