from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class HistoryView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un client")
        self.duplicate_button = QPushButton("Dupliquer")
        filters.addWidget(self.search_input)
        filters.addWidget(self.duplicate_button)
        self.quote_table = QTableWidget(0, 4)
        self.quote_table.setHorizontalHeaderLabels(["ID", "Date", "Client", "Montant"])
        layout.addLayout(filters)
        layout.addWidget(self.quote_table)
