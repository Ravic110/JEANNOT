from pathlib import Path

from PySide6.QtWidgets import QApplication

from devis_batiment.app import create_main_window
from devis_batiment.ui.admin_view import AdminView
from devis_batiment.ui.history_view import HistoryView
from devis_batiment.ui.main_window import MainWindow


def test_main_window_contains_core_tabs(qtbot):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    qtbot.addWidget(window)

    labels = [window.tabs.tabText(index) for index in range(window.tabs.count())]
    assert labels == ["Nouveau devis", "Resultat", "Historique", "Administration"]


def test_admin_and_history_views_expose_main_tables(qtbot):
    app = QApplication.instance() or QApplication([])
    admin_view = AdminView()
    history_view = HistoryView()
    qtbot.addWidget(admin_view)
    qtbot.addWidget(history_view)

    assert admin_view.pricing_table.columnCount() == 3
    assert history_view.quote_table.columnCount() == 4


def test_create_main_window_bootstraps_database_and_services(tmp_path: Path, qtbot):
    app = QApplication.instance() or QApplication([])
    window = create_main_window(tmp_path / "desktop.db")
    qtbot.addWidget(window)

    assert window.database.path.name == "desktop.db"
    assert window.tabs.count() == 4
