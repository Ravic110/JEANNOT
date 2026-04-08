from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QVBoxLayout, QWidget


class HistoryView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.quote_table = QTableWidget(0, 4)
        self.quote_table.setHorizontalHeaderLabels(["ID", "Date", "Client", "Montant"])
        layout.addWidget(self.quote_table)
