from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.services import ClientService


class ClientsView(QWidget):
    def __init__(self, client_service: ClientService | None = None) -> None:
        super().__init__()
        self.client_service = client_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        controls = QHBoxLayout()
        self.add_button = QPushButton("+ Ajouter un client")
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.setEnabled(False)
        controls.addWidget(self.add_button)
        controls.addWidget(self.delete_button)
        controls.addStretch()

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Contact", "Date"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addLayout(controls)
        layout.addWidget(self.table)

        self.add_button.clicked.connect(self._add_client)
        self.delete_button.clicked.connect(self._delete_client)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    def refresh(self) -> None:
        if self.client_service is None:
            return
        clients = self.client_service.list_clients()
        self.table.setRowCount(len(clients))
        for i, client in enumerate(clients):
            self.table.setItem(i, 0, QTableWidgetItem(str(client["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(client["name"])))
            self.table.setItem(i, 2, QTableWidgetItem(str(client["contact"] or "—")))
            self.table.setItem(i, 3, QTableWidgetItem(str(client["created_at"])[:19].replace("T", " ")))
        self.table.resizeColumnsToContents()
        self.delete_button.setEnabled(False)

    def _on_selection_changed(self) -> None:
        self.delete_button.setEnabled(bool(self.table.selectedItems()))

    def _add_client(self) -> None:
        if self.client_service is None:
            return
        dialog = _ClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.client_service.save_client(dialog.name.text().strip(), dialog.contact.text().strip())
            self.refresh()

    def _delete_client(self) -> None:
        if self.client_service is None:
            return
        row = self.table.currentRow()
        if row < 0:
            return
        client_id = int(self.table.item(row, 0).text())
        self.client_service.delete_client(client_id)
        self.refresh()


class _ClientDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ajouter un client")

        form = QFormLayout(self)
        self.name = QLineEdit()
        self.contact = QLineEdit()

        form.addRow("Nom du client", self.name)
        form.addRow("Contact", self.contact)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
