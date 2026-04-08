from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.models import QuoteEstimate, QuoteInput

_CATEGORY_LABELS = {
    "location": "Localisation",
    "structure_type": "Type de structure",
    "roof_type": "Type de toiture",
    "complexity": "Complexité",
    "floors": "Nombre d'étages",
}


def _fmt_mga(amount: float) -> str:
    return f"{amount:,.0f} Ar".replace(",", " ")


class QuoteResultWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self._main_layout = QVBoxLayout(container)
        self._main_layout.setSpacing(12)

        self._placeholder = QLabel("Le résultat du devis apparaîtra ici après le calcul.")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: gray; font-size: 13px;")
        self._main_layout.addWidget(self._placeholder)
        self._main_layout.addStretch()

        self._result_container = QWidget()
        self._result_container.setVisible(False)
        result_layout = QVBoxLayout(self._result_container)
        result_layout.setSpacing(12)

        # --- En-tête : montant total ---
        total_frame = QFrame()
        total_frame.setFrameShape(QFrame.Shape.StyledPanel)
        total_frame.setStyleSheet(
            "QFrame { background-color: #eaf1fb; border: 1px solid #b3cef5; border-radius: 6px; }"
        )
        total_layout = QVBoxLayout(total_frame)
        self._quote_id_label = QLabel()
        self._quote_id_label.setStyleSheet("color: #666; font-size: 11px;")
        self._total_label = QLabel()
        self._total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._total_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a3a6e;")
        total_layout.addWidget(self._quote_id_label)
        total_layout.addWidget(self._total_label)

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

        result_layout.addWidget(total_frame)
        result_layout.addWidget(info_group)
        result_layout.addWidget(coeff_group)
        result_layout.addWidget(breakdown_group)
        result_layout.addStretch()

        self._main_layout.addWidget(self._result_container)

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

    def show_result(self, quote_id: int, quote_input: QuoteInput, estimate: QuoteEstimate) -> None:
        self._placeholder.setVisible(False)
        self._result_container.setVisible(True)

        self._quote_id_label.setText(f"Devis N° {quote_id}")
        self._total_label.setText(f"Montant total estimé : {_fmt_mga(estimate.total_amount)}")

        # Récapitulatif
        info_rows = [
            ("Client", quote_input.client_name),
            ("Contact", quote_input.client_contact or "—"),
            ("Type de bâtiment", quote_input.building_type),
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
            pct_item = QTableWidgetItem(
                f"{estimate.applied_multipliers.get('__pct__', amount / estimate.total_amount * 100):.0f} %"
                if False
                else f"{amount / estimate.total_amount * 100:.0f} %"
            )
            pct_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._breakdown_table.setItem(i, 1, pct_item)
            amt_item = QTableWidgetItem(_fmt_mga(amount))
            amt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._breakdown_table.setItem(i, 2, amt_item)
        self._breakdown_table.resizeRowsToContents()
        self._breakdown_table.setFixedHeight(
            self._breakdown_table.verticalHeader().length()
            + self._breakdown_table.horizontalHeader().height()
            + 4
        )

    def clear(self) -> None:
        self._result_container.setVisible(False)
        self._placeholder.setVisible(True)
