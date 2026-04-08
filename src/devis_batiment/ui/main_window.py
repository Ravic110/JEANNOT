from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMainWindow, QTabWidget

from devis_batiment.ui.quote_form import QuoteFormWidget
from devis_batiment.ui.quote_result import QuoteResultWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jeannot Devis Batiment")
        self.tabs = QTabWidget()
        self.tabs.addTab(QuoteFormWidget(), "Nouveau devis")
        self.tabs.addTab(QuoteResultWidget(), "Resultat")
        self.tabs.addTab(QLabel("Historique"), "Historique")
        self.tabs.addTab(QLabel("Administration"), "Administration")
        self.setCentralWidget(self.tabs)
