from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.config import CLIENT_TYPES
from devis_batiment.services import ClientService
from devis_batiment.ui.formatting import format_amount


class ClientsView(QWidget):
    def __init__(self, client_service: ClientService | None = None) -> None:
        super().__init__()
        self.client_service = client_service
        self._currency = "Ar"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        controls = QHBoxLayout()
        self.add_button = QPushButton("+ Ajouter un client")
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.setEnabled(False)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un nom...")
        self.search_input.setClearButtonEnabled(True)
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tous", *CLIENT_TYPES])
        controls.addWidget(self.add_button)
        controls.addWidget(self.delete_button)
        controls.addStretch()
        controls.addWidget(QLabel("Type :"))
        controls.addWidget(self.type_filter)
        controls.addWidget(QLabel("Recherche :"))
        controls.addWidget(self.search_input)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nom", "Type", "Téléphone", "Email", "Date"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        quotes_group = QGroupBox("Devis du client sélectionné")
        quotes_layout = QVBoxLayout(quotes_group)
        self.quotes_table = QTableWidget(0, 4)
        self.quotes_table.setHorizontalHeaderLabels(["N°", "Date", "Montant", "Statut"])
        self.quotes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.quotes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.quotes_table.setAlternatingRowColors(True)
        self.quotes_table.horizontalHeader().setStretchLastSection(True)
        self.quotes_table.setMaximumHeight(180)
        quotes_layout.addWidget(self.quotes_table)

        layout.addLayout(controls)
        layout.addWidget(self.table, stretch=1)
        layout.addWidget(quotes_group)

        self.add_button.clicked.connect(self._add_client)
        self.delete_button.clicked.connect(self._delete_client)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.search_input.textChanged.connect(self.refresh)
        self.type_filter.currentIndexChanged.connect(self.refresh)

    def set_currency(self, currency: str) -> None:
        self._currency = currency or "Ar"

    def refresh(self) -> None:
        if self.client_service is None:
            return
        search = self.search_input.text().strip() or None
        chosen_type = self.type_filter.currentText()
        client_type = None if chosen_type == "Tous" else chosen_type
        clients = self.client_service.list_clients(search=search, client_type=client_type)
        self.table.setRowCount(len(clients))
        for i, client in enumerate(clients):
            id_item = QTableWidgetItem(str(client["id"]))
            id_item.setData(Qt.ItemDataRole.UserRole, client["id"])
            self.table.setItem(i, 0, id_item)
            self.table.setItem(i, 1, QTableWidgetItem(str(client["name"])))
            self.table.setItem(i, 2, QTableWidgetItem(str(client["client_type"])))
            self.table.setItem(i, 3, QTableWidgetItem(str(client["phone"] or client["contact"] or "—")))
            self.table.setItem(i, 4, QTableWidgetItem(str(client["email"] or "—")))
            self.table.setItem(i, 5, QTableWidgetItem(str(client["created_at"])[:19].replace("T", " ")))
        self.table.resizeColumnsToContents()
        self.delete_button.setEnabled(False)
        self.quotes_table.setRowCount(0)

    def _on_selection_changed(self) -> None:
        self.delete_button.setEnabled(bool(self.table.selectedItems()))
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            return
        client_id = int(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole))
        self.show_client_quotes(client_id)

    def show_client_quotes(self, client_id: int) -> None:
        if self.client_service is None:
            return
        quotes = self.client_service.list_quotes_for_client(client_id)
        self.quotes_table.setRowCount(len(quotes))
        for i, quote in enumerate(quotes):
            self.quotes_table.setItem(i, 0, QTableWidgetItem(str(quote["id"])))
            date_str = str(quote["created_at"])[:19].replace("T", " ")
            self.quotes_table.setItem(i, 1, QTableWidgetItem(date_str))
            self.quotes_table.setItem(
                i, 2, QTableWidgetItem(format_amount(float(quote["total_amount"]), self._currency))
            )
            self.quotes_table.setItem(i, 3, QTableWidgetItem(str(quote.get("status", "Brouillon"))))
        self.quotes_table.resizeColumnsToContents()

    def _add_client(self) -> None:
        if self.client_service is None:
            return
        dialog = _ClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.values()
            if not values["name"]:
                return
            self.client_service.save_client(**values)
            self.refresh()

    def _delete_client(self) -> None:
        if self.client_service is None:
            return
        row = self.table.currentRow()
        if row < 0:
            return
        client_id = int(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole))
        self.client_service.delete_client(client_id)
        self.refresh()


class _ClientDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ajouter un client")

        form = QFormLayout(self)
        self.name = QLineEdit()
        self.client_type = QComboBox()
        self.client_type.addItems(CLIENT_TYPES)
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.address = QLineEdit()
        self.site_address = QLineEdit()
        self.notes = QLineEdit()

        form.addRow("Nom du client *", self.name)
        form.addRow("Type", self.client_type)
        form.addRow("E-mail", self.email)
        form.addRow("Téléphone", self.phone)
        form.addRow("Adresse", self.address)
        form.addRow("Adresse de chantier", self.site_address)
        form.addRow("Notes", self.notes)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self) -> dict[str, str]:
        return {
            "name": self.name.text().strip(),
            "client_type": self.client_type.currentText(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "address": self.address.text().strip(),
            "site_address": self.site_address.text().strip(),
            "notes": self.notes.text().strip(),
            "contact": self.phone.text().strip(),
        }
