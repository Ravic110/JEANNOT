from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.services.calcul_btp import MissingMaterialPriceError
from devis_batiment.models import QuoteInput
from devis_batiment.services import (
    AdminService,
    ClientService,
    ProjectService,
    QuoteService,
    QuoteWorkflow,
    SettingsService,
)
from devis_batiment.storage import Database
from devis_batiment.ui.admin_view import AdminView
from devis_batiment.ui.clients_view import ClientsView
from devis_batiment.ui.dashboard_view import DashboardView
from devis_batiment.ui.history_view import HistoryView
from devis_batiment.ui.materials_view import MaterialsView
from devis_batiment.ui.projects_view import ProjectsView
from devis_batiment.ui.quote_form import QuoteFormWidget
from devis_batiment.ui.quote_result import QuoteResultWidget
from devis_batiment.ui.settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self, database: Database | None = None) -> None:
        super().__init__()
        self.database = database or Database(Path(":memory:"))
        self.database.initialize()

        self.admin_service = AdminService(self.database)
        self.quote_service = QuoteService(self.database)
        self.quote_workflow = QuoteWorkflow(self.database)
        self.settings_service = SettingsService(self.database)
        self.client_service = ClientService(self.database)
        self.project_service = ProjectService(self.database)

        self.admin_service.seed_defaults_if_empty()

        self.setWindowTitle("SmartBTP Devis Desktop")
        self.resize(1080, 760)
        self.setMinimumSize(820, 620)

        self._build_ui()

        self.quote_form.quote_requested.connect(self._on_quote_requested)
        self.pages.currentChanged.connect(self._on_page_changed)

    def _build_ui(self) -> None:
        sidebar = QListWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(180)
        sidebar.setSpacing(4)
        for label in ["Dashboard", "Clients", "Projets", "Devis", "Matériaux", "Tarifs", "Paramètres"]:
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            sidebar.addItem(item)

        self.dashboard_view = DashboardView(self.database)
        self.clients_view = ClientsView(self.client_service)
        self.projects_view = ProjectsView(self.project_service)
        self.quote_form = QuoteFormWidget()
        self.quote_result = QuoteResultWidget()
        self.history_view = HistoryView(self.quote_service)
        self.admin_view = AdminView(self.admin_service)
        self.materials_view = MaterialsView(self.admin_service)
        self.settings_view = SettingsView(self.settings_service)

        devis_controls = QStackedWidget()
        devis_controls.addWidget(self.quote_form)
        devis_controls.addWidget(self.quote_result)
        devis_controls.addWidget(self.history_view)
        self.devis_tabs = devis_controls

        devis_page = QWidget()
        devis_layout = QVBoxLayout(devis_page)
        devis_layout.setContentsMargins(0, 0, 0, 0)
        devis_layout.addWidget(self.devis_tabs)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.dashboard_view)
        self.pages.addWidget(self.clients_view)
        self.pages.addWidget(self.projects_view)
        self.pages.addWidget(devis_page)
        self.pages.addWidget(self.materials_view)
        self.pages.addWidget(self.admin_view)
        self.pages.addWidget(self.settings_view)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(sidebar)
        content_layout.addWidget(self.pages, stretch=1)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(QLabel("SmartBTP Devis Desktop"))
        root_layout.addWidget(content)

        self.setCentralWidget(root)
        self.sidebar = sidebar
        sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        sidebar.setCurrentRow(0)

    def _on_quote_requested(self, quote_input: QuoteInput) -> None:
        try:
            quote_id, estimate = self.quote_workflow.create_quote(quote_input)
        except MissingMaterialPriceError as exc:
            QMessageBox.warning(self, "Prix de matériaux manquants", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "Erreur de calcul", f"Une erreur inattendue s'est produite :\n{exc}")
            return

        self.quote_result.set_currency(self.settings_service.get("currency") or "Ar")
        self.quote_result.show_result(quote_id, quote_input, estimate)
        self.devis_tabs.setCurrentIndex(1)
        self.pages.setCurrentIndex(3)
        self.history_view.refresh()

    def _on_page_changed(self, index: int) -> None:
        currency = self.settings_service.get("currency") or "Ar"
        if index == 0:
            self.dashboard_view.set_currency(currency)
            self.dashboard_view.refresh()
        elif index == 1:
            self.clients_view.refresh()
        elif index == 2:
            self.projects_view.refresh()
        elif index == 3:
            self.history_view.set_currency(currency)
        elif index == 4:
            self.materials_view.refresh()
        elif index == 5:
            self.admin_view.refresh()
        elif index == 6:
            self.settings_view.load()
