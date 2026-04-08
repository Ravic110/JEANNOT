from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.services import QuoteService


def _fmt_mga(amount: float) -> str:
    return f"{amount:,.0f} Ar".replace(",", " ")


class HistoryView(QWidget):
    open_quote_requested = Signal(int)  # émet l'id du devis à ouvrir

    def __init__(self, quote_service: QuoteService | None = None) -> None:
        super().__init__()
        self.quote_service = quote_service

        layout = QVBoxLayout(self)

        # Barre de recherche et actions
        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un client...")
        self.search_input.setClearButtonEnabled(True)
        self.refresh_button = QPushButton("Actualiser")
        self.duplicate_button = QPushButton("Dupliquer")
        self.duplicate_button.setEnabled(False)
        filters.addWidget(QLabel("Recherche :"))
        filters.addWidget(self.search_input, stretch=1)
        filters.addWidget(self.refresh_button)
        filters.addWidget(self.duplicate_button)

        self.quote_table = QTableWidget(0, 4)
        self.quote_table.setHorizontalHeaderLabels(["ID", "Date", "Client", "Montant (Ar)"])
        self.quote_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.quote_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.quote_table.horizontalHeader().setStretchLastSection(True)
        self.quote_table.setAlternatingRowColors(True)

        layout.addLayout(filters)
        layout.addWidget(self.quote_table)

        self.search_input.textChanged.connect(self._on_search)
        self.refresh_button.clicked.connect(self.refresh)
        self.duplicate_button.clicked.connect(self._on_duplicate)
        self.quote_table.itemSelectionChanged.connect(self._on_selection_changed)

    def set_service(self, quote_service: QuoteService) -> None:
        self.quote_service = quote_service
        self.refresh()

    def refresh(self) -> None:
        if self.quote_service is None:
            return
        term = self.search_input.text().strip()
        if term:
            rows = self.quote_service.search_quotes(term)
        else:
            rows = self.quote_service.list_quotes()
        self._populate(rows)

    def _on_search(self, text: str) -> None:
        if self.quote_service is None:
            return
        if text.strip():
            rows = self.quote_service.search_quotes(text.strip())
        else:
            rows = self.quote_service.list_quotes()
        self._populate(rows)

    def _populate(self, rows: list[dict[str, object]]) -> None:
        self.quote_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            id_item = QTableWidgetItem(str(row["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setData(Qt.ItemDataRole.UserRole, row["id"])
            self.quote_table.setItem(i, 0, id_item)

            date_str = str(row["created_at"])[:19].replace("T", " ")
            self.quote_table.setItem(i, 1, QTableWidgetItem(date_str))
            self.quote_table.setItem(i, 2, QTableWidgetItem(str(row["client_name"])))

            amt_item = QTableWidgetItem(_fmt_mga(float(row["total_amount"])))
            amt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.quote_table.setItem(i, 3, amt_item)

        self.quote_table.resizeColumnsToContents()

    def _on_selection_changed(self) -> None:
        self.duplicate_button.setEnabled(bool(self.quote_table.selectedItems()))

    def _on_duplicate(self) -> None:
        if self.quote_service is None:
            return
        selected = self.quote_table.selectedItems()
        if not selected:
            return
        row_idx = self.quote_table.currentRow()
        id_item = self.quote_table.item(row_idx, 0)
        if id_item is None:
            return
        quote_id = int(id_item.data(Qt.ItemDataRole.UserRole))
        try:
            new_id = self.quote_service.duplicate_quote(quote_id)
            self.refresh()
            QMessageBox.information(
                self,
                "Duplication réussie",
                f"Le devis N° {quote_id} a été dupliqué (nouveau N° {new_id}).",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", f"Impossible de dupliquer le devis :\n{exc}")
