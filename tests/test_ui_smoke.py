from pathlib import Path

from PySide6.QtWidgets import QApplication

from devis_batiment.app import create_main_window
from devis_batiment.ui.admin_view import AdminView
from devis_batiment.ui.history_view import HistoryView
from devis_batiment.ui.main_window import MainWindow


def test_main_window_contains_sidebar_sections(qtbot):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    qtbot.addWidget(window)

    labels = [window.sidebar.item(i).text() for i in range(window.sidebar.count())]
    assert labels == ["Dashboard", "Clients", "Projets", "Devis", "Matériaux", "Tarifs", "Paramètres"]


def test_admin_and_history_views_expose_main_tables(qtbot):
    app = QApplication.instance() or QApplication([])
    admin_view = AdminView()
    history_view = HistoryView()
    qtbot.addWidget(admin_view)
    qtbot.addWidget(history_view)

    assert admin_view.adjustment_table.columnCount() == 3
    assert history_view.quote_table.columnCount() == 4


def test_create_main_window_bootstraps_database_and_services(tmp_path: Path, qtbot):
    app = QApplication.instance() or QApplication([])
    window = create_main_window(tmp_path / "desktop.db")
    qtbot.addWidget(window)

    assert window.database.path.name == "desktop.db"
    assert window.sidebar.count() == 7


def test_format_amount_uses_currency_and_space_separator():
    from devis_batiment.ui.formatting import format_amount

    assert format_amount(1_234_567) == "1 234 567 Ar"
    assert format_amount(1000, "MGA") == "1 000 MGA"
    assert format_amount(0) == "0 Ar"


def test_open_quote_from_history_shows_result(qtbot):
    from pathlib import Path
    from devis_batiment.models import MaterialLine, QuoteEstimate, QuoteInput
    from devis_batiment.storage import Database
    from devis_batiment.ui.main_window import MainWindow

    window = MainWindow(Database(Path(":memory:")))
    qtbot.addWidget(window)

    quote_input = QuoteInput(
        client_name="Client Test", client_contact="", project_name="P",
        project_type="Maison", location="Antananarivo", surface_m2=100,
        length_m=0.0, width_m=0.0, height_m=0.0, thickness_m=0.0, floors=1,
        structure_type="Béton armé", roof_type="Tôle", room_count=3,
        finish_level="Standard", complexity="Simple",
    )
    estimate = QuoteEstimate(
        total_amount=12_000_000.0, applied_multipliers={"Marge de sécurité": 1.0},
        breakdown={"Matériaux": 12_000_000.0},
        materials=[MaterialLine("Ciment", "sacs", 10, 45_000, 450_000)],
        volume_m3=5.0,
    )
    saved_id = window.quote_service.save_quote(quote_input, estimate)

    window._on_open_quote_requested(saved_id)

    assert window.pages.currentIndex() == 3
    assert window.devis_tabs.currentIndex() == 1
    assert "12 000 000" in window.quote_result._total_label.text()
