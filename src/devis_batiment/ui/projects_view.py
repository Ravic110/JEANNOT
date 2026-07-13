from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.config import PROJECT_TYPES
from devis_batiment.services import ProjectService


class ProjectsView(QWidget):
    def __init__(self, project_service: ProjectService | None = None) -> None:
        super().__init__()
        self.project_service = project_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        controls = QHBoxLayout()
        self.add_button = QPushButton("+ Ajouter un projet")
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.setEnabled(False)
        controls.addWidget(self.add_button)
        controls.addWidget(self.delete_button)
        controls.addStretch()

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Client", "Projet", "Type", "Localisation"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addLayout(controls)
        layout.addWidget(self.table)

        self.add_button.clicked.connect(self._add_project)
        self.delete_button.clicked.connect(self._delete_project)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    def refresh(self) -> None:
        if self.project_service is None:
            return
        projects = self.project_service.list_projects()
        self.table.setRowCount(len(projects))
        for i, project in enumerate(projects):
            self.table.setItem(i, 0, QTableWidgetItem(str(project["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(project["client_name"])))
            self.table.setItem(i, 2, QTableWidgetItem(str(project["project_name"] or "—")))
            self.table.setItem(i, 3, QTableWidgetItem(str(project["project_type"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(project["location"] or "—")))
        self.table.resizeColumnsToContents()
        self.delete_button.setEnabled(False)

    def _on_selection_changed(self) -> None:
        self.delete_button.setEnabled(bool(self.table.selectedItems()))

    def _add_project(self) -> None:
        if self.project_service is None:
            return
        dialog = _ProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.project_service.save_project(
                dialog.client_name.text().strip(),
                dialog.client_contact.text().strip(),
                dialog.project_name.text().strip(),
                dialog.project_type.currentText(),
                dialog.location.text().strip(),
                dialog.notes.text().strip(),
            )
            self.refresh()

    def _delete_project(self) -> None:
        if self.project_service is None:
            return
        row = self.table.currentRow()
        if row < 0:
            return
        project_id = int(self.table.item(row, 0).text())
        self.project_service.delete_project(project_id)
        self.refresh()


class _ProjectDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ajouter un projet")

        form = QFormLayout(self)
        self.client_name = QLineEdit()
        self.client_contact = QLineEdit()
        self.project_name = QLineEdit()
        self.project_type = QComboBox()
        self.project_type.addItems(PROJECT_TYPES)
        self.location = QLineEdit()
        self.notes = QLineEdit()

        form.addRow("Nom du client", self.client_name)
        form.addRow("Contact", self.client_contact)
        form.addRow("Nom du projet", self.project_name)
        form.addRow("Type de chantier", self.project_type)
        form.addRow("Localisation", self.location)
        form.addRow("Notes", self.notes)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
