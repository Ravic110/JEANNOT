from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QTabWidget, QVBoxLayout, QWidget


class AdminView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.pricing_table = QTableWidget(0, 3)
        self.pricing_table.setHorizontalHeaderLabels(["Type", "Finition", "Prix/m2"])
        self.adjustment_table = QTableWidget(0, 3)
        self.adjustment_table.setHorizontalHeaderLabels(["Categorie", "Cle", "Coefficient"])
        self.breakdown_table = QTableWidget(0, 2)
        self.breakdown_table.setHorizontalHeaderLabels(["Lot", "Pourcentage"])
        self.tabs.addTab(self.pricing_table, "Prix")
        self.tabs.addTab(self.adjustment_table, "Coefficients")
        self.tabs.addTab(self.breakdown_table, "Repartition")
        layout.addWidget(self.tabs)
