from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.config import (
    COMPLEXITY_LEVELS,
    LOCATIONS,
    ROOF_TYPES,
    STRUCTURE_TYPES,
)
from devis_batiment.services import AdminService


class AdminView(QWidget):
    def __init__(self, admin_service: AdminService | None = None) -> None:
        super().__init__()
        self.admin_service = admin_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        self.tabs = QTabWidget()

        # Tab 1 : Coefficients
        self.adjustment_table = QTableWidget(0, 3)
        self.adjustment_table.setHorizontalHeaderLabels(["Catégorie", "Valeur", "Coefficient"])
        self.adjustment_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.adjustment_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.adjustment_table.horizontalHeader().setStretchLastSection(True)
        self.adjustment_table.setAlternatingRowColors(True)
        self.tabs.addTab(self._wrap_with_buttons(self.adjustment_table, self._add_adjustment, self._del_adjustment), "Coefficients")

        # Tab 2 : Répartition
        self.breakdown_table = QTableWidget(0, 2)
        self.breakdown_table.setHorizontalHeaderLabels(["Poste de travaux", "Pourcentage (%)"])
        self.breakdown_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.breakdown_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.breakdown_table.horizontalHeader().setStretchLastSection(True)
        self.breakdown_table.setAlternatingRowColors(True)
        self.tabs.addTab(self._wrap_with_buttons(self.breakdown_table, self._add_breakdown, self._del_breakdown), "Répartition")

        layout.addWidget(self.tabs)

    def _wrap_with_buttons(
        self,
        table: QTableWidget,
        add_fn: object,
        del_fn: object,
    ) -> QWidget:
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        btn_bar = QHBoxLayout()
        add_btn = QPushButton("+ Ajouter")
        add_btn.setProperty("class", "primary")
        del_btn = QPushButton("Supprimer")
        del_btn.setProperty("class", "danger")
        del_btn.setEnabled(False)
        refresh_btn = QPushButton("Actualiser")
        btn_bar.addWidget(add_btn)
        btn_bar.addWidget(del_btn)
        btn_bar.addStretch()
        btn_bar.addWidget(refresh_btn)
        vbox.addLayout(btn_bar)
        vbox.addWidget(table)

        add_btn.clicked.connect(add_fn)
        del_btn.clicked.connect(del_fn)
        refresh_btn.clicked.connect(self.refresh)
        table.itemSelectionChanged.connect(lambda: del_btn.setEnabled(bool(table.selectedItems())))

        return widget

    def set_service(self, admin_service: AdminService) -> None:
        self.admin_service = admin_service
        self.refresh()

    def refresh(self) -> None:
        if self.admin_service is None:
            return
        self._load_adjustments()
        self._load_breakdown()

    def _load_adjustments(self) -> None:
        rows = self.admin_service.list_adjustment_rules()
        self.adjustment_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.adjustment_table.setItem(i, 0, QTableWidgetItem(str(row["category"])))
            self.adjustment_table.setItem(i, 1, QTableWidgetItem(str(row["rule_key"])))
            coeff = QTableWidgetItem(f"{float(row['multiplier']):.3f}")
            coeff.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.adjustment_table.setItem(i, 2, coeff)
        self.adjustment_table.resizeColumnsToContents()

    def _load_breakdown(self) -> None:
        rows = self.admin_service.list_breakdown_rules()
        self.breakdown_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.breakdown_table.setItem(i, 0, QTableWidgetItem(str(row["lot_name"])))
            pct = QTableWidgetItem(f"{float(row['percentage']) * 100:.1f}")
            pct.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.breakdown_table.setItem(i, 1, pct)
        self.breakdown_table.resizeColumnsToContents()

    # --- Ajouts ---

    def _add_adjustment(self) -> None:
        if self.admin_service is None:
            return
        dlg = _AdjustmentDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                self.admin_service.save_adjustment_rule(
                    dlg.category.currentData(),
                    dlg.rule_key.text().strip(),
                    dlg.multiplier.value(),
                )
                self._load_adjustments()
            except Exception as exc:
                QMessageBox.critical(self, "Erreur", str(exc))

    def _add_breakdown(self) -> None:
        if self.admin_service is None:
            return
        dlg = _BreakdownDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                self.admin_service.save_breakdown_rule(
                    dlg.lot_name.text().strip(),
                    dlg.percentage.value() / 100.0,
                )
                self._load_breakdown()
            except Exception as exc:
                QMessageBox.critical(self, "Erreur", str(exc))

    # --- Suppressions ---

    def _del_adjustment(self) -> None:
        if self.admin_service is None:
            return
        row = self.adjustment_table.currentRow()
        if row < 0:
            return
        category = self.adjustment_table.item(row, 0).text()
        rule_key = self.adjustment_table.item(row, 1).text()
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer la règle « {category} = {rule_key} » ?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.admin_service.delete_adjustment_rule(category, rule_key)
            self._load_adjustments()

    def _del_breakdown(self) -> None:
        if self.admin_service is None:
            return
        row = self.breakdown_table.currentRow()
        if row < 0:
            return
        lot_name = self.breakdown_table.item(row, 0).text()
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer le poste « {lot_name} » ?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.admin_service.delete_breakdown_rule(lot_name)
            self._load_breakdown()


# ---------------------------------------------------------------------------
# Dialogues d'ajout
# ---------------------------------------------------------------------------

class _AdjustmentDialog(QDialog):
    _CATEGORIES = [
        ("location", "Localisation", LOCATIONS),
        ("structure_type", "Type de structure", STRUCTURE_TYPES),
        ("roof_type", "Type de toiture", ROOF_TYPES),
        ("complexity", "Complexité", COMPLEXITY_LEVELS),
        ("floors", "Nombre d'étages", ["1", "2", "3", "4", "5+"]),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ajouter un coefficient")
        form = QFormLayout(self)

        self.category = QComboBox()
        for key, label, _ in self._CATEGORIES:
            self.category.addItem(label, key)

        self.rule_key = QLineEdit()
        self.rule_key.setPlaceholderText("Valeur (ex: Antananarivo, Tuile...)")

        self.multiplier = QDoubleSpinBox()
        self.multiplier.setMinimum(0.01)
        self.multiplier.setMaximum(10.0)
        self.multiplier.setDecimals(3)
        self.multiplier.setSingleStep(0.01)
        self.multiplier.setValue(1.0)

        form.addRow("Catégorie", self.category)
        form.addRow("Valeur", self.rule_key)
        form.addRow("Coefficient (×)", self.multiplier)
        form.addRow(QLabel("<i>Valeur 1.0 = pas d'ajustement</i>"))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self.category.currentIndexChanged.connect(self._on_category_changed)
        self._on_category_changed(0)

    def _on_category_changed(self, _: int) -> None:
        key = self.category.currentData()
        for cat_key, _, suggestions in self._CATEGORIES:
            if cat_key == key:
                self.rule_key.setPlaceholderText(" | ".join(suggestions))
                break

    def _on_accept(self) -> None:
        if not self.rule_key.text().strip():
            QMessageBox.warning(self, "Erreur", "La valeur est obligatoire.")
            return
        # Stocker la clé interne (pas le label)
        self.category.setCurrentIndex(self.category.currentIndex())
        self.accept()

    # Override currentText pour retourner la clé interne
    class _CategoryCombo(QComboBox):
        def currentText(self) -> str:  # type: ignore[override]
            return self.currentData() or super().currentText()


class _BreakdownDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ajouter un poste de répartition")
        form = QFormLayout(self)

        self.lot_name = QLineEdit()
        self.lot_name.setPlaceholderText("Ex: Terrassement et fondations")

        self.percentage = QDoubleSpinBox()
        self.percentage.setMinimum(0.1)
        self.percentage.setMaximum(100.0)
        self.percentage.setDecimals(1)
        self.percentage.setSingleStep(0.5)
        self.percentage.setValue(5.0)
        self.percentage.setSuffix(" %")

        form.addRow("Nom du poste", self.lot_name)
        form.addRow("Pourcentage", self.percentage)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _on_accept(self) -> None:
        if not self.lot_name.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du poste est obligatoire.")
            return
        self.accept()
