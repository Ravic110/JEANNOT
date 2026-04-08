from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from devis_batiment.ui.admin_view import AdminView
from devis_batiment.ui.history_view import HistoryView
from devis_batiment.ui.quote_form import QuoteFormWidget
from devis_batiment.ui.quote_result import QuoteResultWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jeannot Devis Batiment")
        self.tabs = QTabWidget()
        self.tabs.addTab(QuoteFormWidget(), "Nouveau devis")
        self.tabs.addTab(QuoteResultWidget(), "Resultat")
        self.tabs.addTab(HistoryView(), "Historique")
        self.tabs.addTab(AdminView(), "Administration")
        self.setCentralWidget(self.tabs)
