from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.services import AdminService


class MaterialsView(QWidget):
    def __init__(self, admin_service: AdminService | None = None) -> None:
        super().__init__()
        self.admin_service = admin_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        controls = QHBoxLayout()
        self.add_button = QPushButton("+ Ajouter un matériau")
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.setEnabled(False)
        controls.addWidget(self.add_button)
        controls.addWidget(self.delete_button)
        controls.addStretch()

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Matériau", "Unité", "Prix unitaire (Ar)"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addLayout(controls)
        layout.addWidget(self.table)

        self.add_button.clicked.connect(self._add_material)
        self.delete_button.clicked.connect(self._delete_material)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    def refresh(self) -> None:
        if self.admin_service is None:
            return
        materials = self.admin_service.list_materials()
        self.table.setRowCount(len(materials))
        for i, material in enumerate(materials):
            self.table.setItem(i, 0, QTableWidgetItem(str(material["name"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(material["unit"])))
            self.table.setItem(i, 2, QTableWidgetItem(f"{float(material['unit_price']):,.0f}".replace(",", " ")))
        self.table.resizeColumnsToContents()
        self.delete_button.setEnabled(False)

    def _on_selection_changed(self) -> None:
        self.delete_button.setEnabled(bool(self.table.selectedItems()))

    def _add_material(self) -> None:
        if self.admin_service is None:
            return
        dialog = _MaterialDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.admin_service.save_material(
                dialog.name.text().strip(),
                dialog.unit.text().strip(),
                dialog.price.value(),
            )
            self.refresh()

    def _delete_material(self) -> None:
        if self.admin_service is None:
            return
        row = self.table.currentRow()
        if row < 0:
            return
        name = self.table.item(row, 0).text()
        self.admin_service.delete_material(name)
        self.refresh()


class _MaterialDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ajouter un matériau")

        form = QFormLayout(self)
        self.name = QLineEdit()
        self.unit = QLineEdit()
        self.price = QDoubleSpinBox()
        self.price.setMinimum(0.0)
        self.price.setMaximum(10_000_000.0)
        self.price.setDecimals(0)
        self.price.setSingleStep(1_000)
        self.price.setSuffix(" Ar")

        form.addRow("Nom du matériau", self.name)
        form.addRow("Unité", self.unit)
        form.addRow("Prix unitaire", self.price)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
