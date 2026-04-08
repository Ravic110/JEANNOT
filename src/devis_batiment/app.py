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
