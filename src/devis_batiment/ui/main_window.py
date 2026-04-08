from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget, QVBoxLayout, QWidget

from devis_batiment.calculator import MissingReferenceError
from devis_batiment.models import QuoteInput
from devis_batiment.services import AdminService, QuoteService, QuoteWorkflow, SettingsService
from devis_batiment.storage import Database
from devis_batiment.ui.admin_view import AdminView
from devis_batiment.ui.history_view import HistoryView
from devis_batiment.ui.quote_form import QuoteFormWidget
from devis_batiment.ui.quote_result import QuoteResultWidget
from devis_batiment.ui.settings_view import SettingsView

_TAB_FORM = 0
_TAB_RESULT = 1
_TAB_HISTORY = 2
_TAB_ADMIN = 3
_TAB_SETTINGS = 4


class MainWindow(QMainWindow):
    def __init__(self, database: Database | None = None) -> None:
        super().__init__()
        self.database = database or Database(Path(":memory:"))
        self.database.initialize()

        self.admin_service = AdminService(self.database)
        self.quote_service = QuoteService(self.database)
        self.quote_workflow = QuoteWorkflow(self.database)
        self.settings_service = SettingsService(self.database)

        # Seed des données initiales si la base est vide
        self.admin_service.seed_defaults_if_empty()

        self.setWindowTitle("Jeannot — Devis Bâtiment")
        self.resize(980, 720)
        self.setMinimumSize(760, 560)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)
        self.tabs.setContentsMargins(0, 0, 0, 0)

        self.quote_form = QuoteFormWidget()
        self.quote_result = QuoteResultWidget()
        self.history_view = HistoryView(self.quote_service)
        self.admin_view = AdminView(self.admin_service)
        self.settings_view = SettingsView(self.settings_service)

        self.tabs.addTab(self.quote_form, "  Nouveau devis  ")
        self.tabs.addTab(self.quote_result, "  Résultat  ")
        self.tabs.addTab(self.history_view, "  Historique  ")
        self.tabs.addTab(self.admin_view, "  Administration  ")
        self.tabs.addTab(self.settings_view, "  Paramètres  ")

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(12, 10, 12, 12)
        central_layout.setSpacing(0)
        central_layout.addWidget(self.tabs)
        self.setCentralWidget(central)

        # Connexions des signaux
        self.quote_form.quote_requested.connect(self._on_quote_requested)
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_quote_requested(self, quote_input: QuoteInput) -> None:
        try:
            quote_id, estimate = self.quote_workflow.create_quote(quote_input)
        except MissingReferenceError as exc:
            QMessageBox.warning(
                self,
                "Données de référence manquantes",
                str(exc),
            )
            return
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Erreur de calcul",
                f"Une erreur inattendue s'est produite :\n{exc}",
            )
            return

        self.quote_result.show_result(quote_id, quote_input, estimate)
        self.tabs.setCurrentIndex(_TAB_RESULT)
        self.history_view.refresh()

    def _on_tab_changed(self, index: int) -> None:
        if index == _TAB_HISTORY:
            self.history_view.refresh()
        elif index == _TAB_ADMIN:
            self.admin_view.refresh()
        elif index == _TAB_SETTINGS:
            self.settings_view.load()
