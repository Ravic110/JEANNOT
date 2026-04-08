from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QTabWidget

from devis_batiment.services import AdminService, QuoteService, QuoteWorkflow
from devis_batiment.storage import Database
from devis_batiment.ui.admin_view import AdminView
from devis_batiment.ui.history_view import HistoryView
from devis_batiment.ui.quote_form import QuoteFormWidget
from devis_batiment.ui.quote_result import QuoteResultWidget


class MainWindow(QMainWindow):
    def __init__(self, database: Database | None = None) -> None:
        super().__init__()
        self.database = database or Database(Path(":memory:"))
        self.database.initialize()
        self.admin_service = AdminService(self.database)
        self.quote_service = QuoteService(self.database)
        self.quote_workflow = QuoteWorkflow(self.database)
        self.setWindowTitle("Jeannot Devis Batiment")
        self.tabs = QTabWidget()
        self.tabs.addTab(QuoteFormWidget(), "Nouveau devis")
        self.tabs.addTab(QuoteResultWidget(), "Resultat")
        self.tabs.addTab(HistoryView(), "Historique")
        self.tabs.addTab(AdminView(), "Administration")
        self.setCentralWidget(self.tabs)
