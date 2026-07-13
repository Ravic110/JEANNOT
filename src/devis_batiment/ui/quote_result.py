from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.models import QuoteEstimate, QuoteInput
from devis_batiment.ui.formatting import format_amount
from devis_batiment.utils.pdf import export_quote_pdf

_CATEGORY_LABELS = {
    "location": "Localisation",
    "structure_type": "Type de structure",
    "roof_type": "Type de toiture",
    "complexity": "Complexité",
    "floors": "Nombre d'étages",
    "Marge de sécurité": "Marge de sécurité",
}


class QuoteResultWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._currency = "Ar"
        self._settings_service = None
        self._last_quote_id: int | None = None
        self._last_input = None
        self._last_estimate = None
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self._main_layout = QVBoxLayout(container)
        self._main_layout.setSpacing(14)
        self._main_layout.setContentsMargins(16, 16, 16, 16)

        self._placeholder = QLabel("Le résultat du devis apparaîtra ici après le calcul.")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #94A3B8; font-size: 14px;")
        self._main_layout.addWidget(self._placeholder)
        self._main_layout.addStretch()

        self._result_container = QWidget()
        self._result_container.setVisible(False)
        result_layout = QVBoxLayout(self._result_container)
        result_layout.setSpacing(12)

        # --- En-tête : montant total ---
        total_frame = QFrame()
        total_frame.setObjectName("totalFrame")
        total_frame.setFrameShape(QFrame.Shape.StyledPanel)
        total_layout = QVBoxLayout(total_frame)
        self._quote_id_label = QLabel()
        self._quote_id_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;")
        self._total_label = QLabel()
        self._total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._total_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #1E40AF;")
        total_layout.addWidget(self._quote_id_label)
        total_layout.addWidget(self._total_label)

        self._export_button = QPushButton("Exporter en PDF")
        self._export_button.setEnabled(False)
        self._export_button.clicked.connect(self._on_export_pdf)
        total_layout.addWidget(self._export_button)

        # --- Infos client / projet ---
        info_group = QGroupBox("Récapitulatif du projet")
        info_layout = QVBoxLayout(info_group)
        self._info_table = QTableWidget(0, 2)
        self._info_table.horizontalHeader().setVisible(False)
        self._info_table.verticalHeader().setVisible(False)
        self._info_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._info_table.setAlternatingRowColors(True)
        self._info_table.horizontalHeader().setStretchLastSection(True)
        self._info_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        info_layout.addWidget(self._info_table)

        # --- Coefficients appliqués ---
        coeff_group = QGroupBox("Coefficients appliqués")
        coeff_layout = QVBoxLayout(coeff_group)
        self._coeff_table = QTableWidget(0, 2)
        self._coeff_table.setHorizontalHeaderLabels(["Paramètre", "Coefficient"])
        self._coeff_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._coeff_table.horizontalHeader().setStretchLastSection(True)
        self._coeff_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        coeff_layout.addWidget(self._coeff_table)

        # --- Ventilation par lots ---
        breakdown_group = QGroupBox("Ventilation par grands postes")
        breakdown_layout = QVBoxLayout(breakdown_group)
        self._breakdown_table = QTableWidget(0, 3)
        self._breakdown_table.setHorizontalHeaderLabels(["Poste de travaux", "%", "Montant estimé"])
        self._breakdown_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._breakdown_table.horizontalHeader().setStretchLastSection(True)
        self._breakdown_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        breakdown_layout.addWidget(self._breakdown_table)

        # --- Matériaux et main-d'œuvre ---
        materials_group = QGroupBox("Matériaux et main-d'œuvre")
        materials_layout = QVBoxLayout(materials_group)
        self._materials_table = QTableWidget(0, 5)
        self._materials_table.setHorizontalHeaderLabels(["Matériau", "Quantité", "Unité", "Prix unitaire", "Total"])
        self._materials_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._materials_table.setAlternatingRowColors(True)
        self._materials_table.horizontalHeader().setStretchLastSection(True)
        self._materials_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        materials_layout.addWidget(self._materials_table)

        result_layout.addWidget(total_frame)
        result_layout.addWidget(info_group)
        result_layout.addWidget(coeff_group)
        result_layout.addWidget(breakdown_group)
        result_layout.addWidget(materials_group)
        result_layout.addStretch()

        self._main_layout.addWidget(self._result_container)

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

    def set_currency(self, currency: str) -> None:
        self._currency = currency or "Ar"

    def set_settings_service(self, settings_service) -> None:
        self._settings_service = settings_service

    def show_result(self, quote_id: int, quote_input: QuoteInput, estimate: QuoteEstimate) -> None:
        self._last_quote_id = quote_id
        self._last_input = quote_input
        self._last_estimate = estimate
        self._export_button.setEnabled(True)

        self._placeholder.setVisible(False)
        self._result_container.setVisible(True)

        self._quote_id_label.setText(f"Devis N° {quote_id}")
        self._total_label.setText(f"Montant total estimé : {format_amount(estimate.total_amount, self._currency)}")

        # Récapitulatif
        info_rows = [
            ("Client", quote_input.client_name),
            ("Contact", quote_input.client_contact or "—"),
            ("Type de chantier", quote_input.project_type),
            ("Localisation", quote_input.location),
            ("Surface totale", f"{quote_input.surface_m2:.1f} m²"),
            ("Nombre d'étages", str(quote_input.floors)),
            ("Nombre de pièces", str(quote_input.room_count) if quote_input.room_count else "—"),
            ("Type de structure", quote_input.structure_type),
            ("Type de toiture", quote_input.roof_type),
            ("Niveau de finition", quote_input.finish_level),
            ("Complexité", quote_input.complexity),
        ]
        if quote_input.notes:
            info_rows.append(("Observations", quote_input.notes))

        self._info_table.setRowCount(len(info_rows))
        for i, (label, value) in enumerate(info_rows):
            lbl_item = QTableWidgetItem(label)
            lbl_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            lbl_item.setForeground(Qt.GlobalColor.darkGray)
            self._info_table.setItem(i, 0, lbl_item)
            self._info_table.setItem(i, 1, QTableWidgetItem(value))
        self._info_table.resizeRowsToContents()
        self._info_table.setFixedHeight(min(self._info_table.verticalHeader().length() + 4, 300))

        # Coefficients
        self._coeff_table.setRowCount(len(estimate.applied_multipliers))
        for i, (key, value) in enumerate(estimate.applied_multipliers.items()):
            label = _CATEGORY_LABELS.get(key, key)
            self._coeff_table.setItem(i, 0, QTableWidgetItem(label))
            coeff_item = QTableWidgetItem(f"× {value:.3f}")
            coeff_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._coeff_table.setItem(i, 1, coeff_item)
        self._coeff_table.resizeRowsToContents()
        self._coeff_table.setFixedHeight(
            self._coeff_table.verticalHeader().length()
            + self._coeff_table.horizontalHeader().height()
            + 4
        )

        # Ventilation
        self._breakdown_table.setRowCount(len(estimate.breakdown))
        for i, (lot_name, amount) in enumerate(estimate.breakdown.items()):
            self._breakdown_table.setItem(i, 0, QTableWidgetItem(lot_name))
            pct_item = QTableWidgetItem(f"{amount / estimate.total_amount * 100:.0f} %")
            pct_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._breakdown_table.setItem(i, 1, pct_item)
            amt_item = QTableWidgetItem(format_amount(amount, self._currency))
            amt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._breakdown_table.setItem(i, 2, amt_item)
        self._breakdown_table.resizeRowsToContents()
        self._breakdown_table.setFixedHeight(
            self._breakdown_table.verticalHeader().length()
            + self._breakdown_table.horizontalHeader().height()
            + 4
        )

        # Matériaux
        self._materials_table.setRowCount(len(estimate.materials))
        for i, mat in enumerate(estimate.materials):
            self._materials_table.setItem(i, 0, QTableWidgetItem(mat.name))
            qty_item = QTableWidgetItem(f"{mat.quantity:.2f}")
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._materials_table.setItem(i, 1, qty_item)
            self._materials_table.setItem(i, 2, QTableWidgetItem(mat.unit))
            up_item = QTableWidgetItem(format_amount(mat.unit_price, self._currency))
            up_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._materials_table.setItem(i, 3, up_item)
            total_item = QTableWidgetItem(format_amount(mat.line_total, self._currency))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._materials_table.setItem(i, 4, total_item)
        self._materials_table.resizeRowsToContents()
        self._materials_table.setFixedHeight(
            self._materials_table.verticalHeader().length()
            + self._materials_table.horizontalHeader().height()
            + 4
        )

    def clear(self) -> None:
        self._result_container.setVisible(False)
        self._placeholder.setVisible(True)
        self._export_button.setEnabled(False)

    def _on_export_pdf(self) -> None:
        if self._last_estimate is None or self._last_input is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter le devis en PDF",
            f"devis_{self._last_quote_id}.pdf", "PDF (*.pdf)",
        )
        if not path:
            return
        company_info = (
            self._settings_service.get_all() if self._settings_service else {}
        )
        try:
            from pathlib import Path
            export_quote_pdf(
                Path(path), company_info, self._last_quote_id or 0,
                self._last_input, self._last_estimate,
            )
            QMessageBox.information(self, "Export PDF", f"Devis exporté :\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", f"Échec de l'export PDF :\n{exc}")
