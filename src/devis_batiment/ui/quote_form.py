from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.config import (
    BUILDING_TYPES,
    COMPLEXITY_LEVELS,
    FINISH_LEVELS,
    LOCATIONS,
    ROOF_TYPES,
    STRUCTURE_TYPES,
)
from devis_batiment.models import QuoteInput


class QuoteFormWidget(QWidget):
    quote_requested = Signal(object)  # émet un QuoteInput validé

    def __init__(self) -> None:
        super().__init__()
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # --- Groupe : Informations client ---
        client_group = QGroupBox("Informations client")
        client_form = QFormLayout(client_group)
        self.client_name = QLineEdit()
        self.client_name.setPlaceholderText("Nom complet du client *")
        self.client_contact = QLineEdit()
        self.client_contact.setPlaceholderText("Téléphone ou e-mail")
        client_form.addRow("Nom du client *", self.client_name)
        client_form.addRow("Contact", self.client_contact)

        # --- Groupe : Caractéristiques du projet ---
        project_group = QGroupBox("Caractéristiques du projet")
        project_form = QFormLayout(project_group)

        self.building_type = QComboBox()
        self.building_type.addItems(BUILDING_TYPES)

        self.location = QComboBox()
        self.location.addItems(LOCATIONS)

        self.surface_m2 = QDoubleSpinBox()
        self.surface_m2.setMinimum(1.0)
        self.surface_m2.setMaximum(100_000.0)
        self.surface_m2.setDecimals(1)
        self.surface_m2.setSuffix(" m²")
        self.surface_m2.setValue(100.0)

        self.floors = QSpinBox()
        self.floors.setMinimum(1)
        self.floors.setMaximum(50)
        self.floors.setValue(1)
        self.floors.setSuffix(" étage(s)")

        self.room_count = QSpinBox()
        self.room_count.setMinimum(0)
        self.room_count.setMaximum(500)
        self.room_count.setValue(4)
        self.room_count.setSuffix(" pièce(s)")

        project_form.addRow("Type de bâtiment *", self.building_type)
        project_form.addRow("Localisation *", self.location)
        project_form.addRow("Surface totale *", self.surface_m2)
        project_form.addRow("Nombre d'étages *", self.floors)
        project_form.addRow("Nombre de pièces", self.room_count)

        # --- Groupe : Spécifications techniques ---
        tech_group = QGroupBox("Spécifications techniques")
        tech_form = QFormLayout(tech_group)

        self.structure_type = QComboBox()
        self.structure_type.addItems(STRUCTURE_TYPES)

        self.roof_type = QComboBox()
        self.roof_type.addItems(ROOF_TYPES)

        self.finish_level = QComboBox()
        self.finish_level.addItems(FINISH_LEVELS)
        self.finish_level.setCurrentIndex(1)  # Standard par défaut

        self.complexity = QComboBox()
        self.complexity.addItems(COMPLEXITY_LEVELS)
        self.complexity.setCurrentIndex(1)  # Moyenne par défaut

        tech_form.addRow("Type de structure *", self.structure_type)
        tech_form.addRow("Type de toiture *", self.roof_type)
        tech_form.addRow("Niveau de finition *", self.finish_level)
        tech_form.addRow("Complexité *", self.complexity)

        # --- Groupe : Observations ---
        notes_group = QGroupBox("Observations")
        notes_layout = QVBoxLayout(notes_group)
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Remarques, contraintes particulières...")
        self.notes.setMaximumHeight(80)
        notes_layout.addWidget(self.notes)

        # --- Bouton ---
        btn_layout = QHBoxLayout()
        self._required_label = QLabel("* Champs obligatoires")
        self._required_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self.calculate_button = QPushButton("Calculer le devis")
        self.calculate_button.setMinimumHeight(36)
        self.calculate_button.setProperty("class", "primary")
        self.reset_button = QPushButton("Réinitialiser")
        self.reset_button.setMinimumHeight(36)
        btn_layout.addWidget(self._required_label)
        btn_layout.addStretch()
        btn_layout.addWidget(self.reset_button)
        btn_layout.addWidget(self.calculate_button)

        main_layout.addWidget(client_group)
        main_layout.addWidget(project_group)
        main_layout.addWidget(tech_group)
        main_layout.addWidget(notes_group)
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

        self.calculate_button.clicked.connect(self._on_calculate)
        self.reset_button.clicked.connect(self._on_reset)

    def _on_calculate(self) -> None:
        errors = self._validate()
        if errors:
            QMessageBox.warning(
                self,
                "Champs invalides",
                "Veuillez corriger les erreurs suivantes :\n\n" + "\n".join(f"• {e}" for e in errors),
            )
            return
        self.quote_requested.emit(self._build_input())

    def _validate(self) -> list[str]:
        errors: list[str] = []
        if not self.client_name.text().strip():
            errors.append("Le nom du client est obligatoire.")
        if self.surface_m2.value() <= 0:
            errors.append("La surface doit être supérieure à 0 m².")
        if self.floors.value() < 1:
            errors.append("Le nombre d'étages doit être au moins 1.")
        return errors

    def _build_input(self) -> QuoteInput:
        return QuoteInput(
            client_name=self.client_name.text().strip(),
            client_contact=self.client_contact.text().strip(),
            building_type=self.building_type.currentText(),
            location=self.location.currentText(),
            surface_m2=self.surface_m2.value(),
            floors=self.floors.value(),
            structure_type=self.structure_type.currentText(),
            roof_type=self.roof_type.currentText(),
            room_count=self.room_count.value(),
            finish_level=self.finish_level.currentText(),
            complexity=self.complexity.currentText(),
            notes=self.notes.toPlainText().strip(),
        )

    def _on_reset(self) -> None:
        self.client_name.clear()
        self.client_contact.clear()
        self.building_type.setCurrentIndex(0)
        self.location.setCurrentIndex(0)
        self.surface_m2.setValue(100.0)
        self.floors.setValue(1)
        self.room_count.setValue(4)
        self.structure_type.setCurrentIndex(0)
        self.roof_type.setCurrentIndex(0)
        self.finish_level.setCurrentIndex(1)
        self.complexity.setCurrentIndex(1)
        self.notes.clear()

    def populate_from_input(self, quote_input: QuoteInput) -> None:
        """Pré-remplit le formulaire depuis un QuoteInput existant (duplication)."""
        self.client_name.setText(quote_input.client_name)
        self.client_contact.setText(quote_input.client_contact)
        _set_combo(self.building_type, quote_input.building_type)
        _set_combo(self.location, quote_input.location)
        self.surface_m2.setValue(quote_input.surface_m2)
        self.floors.setValue(quote_input.floors)
        self.room_count.setValue(quote_input.room_count)
        _set_combo(self.structure_type, quote_input.structure_type)
        _set_combo(self.roof_type, quote_input.roof_type)
        _set_combo(self.finish_level, quote_input.finish_level)
        _set_combo(self.complexity, quote_input.complexity)
        self.notes.setPlainText(quote_input.notes)


def _set_combo(combo: QComboBox, value: str) -> None:
    idx = combo.findText(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)
