from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
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
    COMPLEXITY_LEVELS,
    FINISH_LEVELS,
    LOCATIONS,
    PROJECT_TYPES,
    ROOF_TYPES,
    STRUCTURE_TYPES,
)
from devis_batiment.models import QuoteInput


class QuoteFormWidget(QWidget):
    quote_requested = Signal(object)
    save_template_requested = Signal(str, object)

    def __init__(self) -> None:
        super().__init__()
        self._applying_template = False
        self._templates: dict[str, dict] = {}
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # --- Ligne : modèles de devis ---
        template_group = QGroupBox("Modèle de devis")
        template_row = QHBoxLayout(template_group)
        self._no_template_label = "— Aucun modèle —"
        self.template_selector = QComboBox()
        self.template_selector.addItem(self._no_template_label)
        self.apply_template_button = QPushButton("Appliquer")
        self.save_template_button = QPushButton("Enregistrer comme modèle")
        template_row.addWidget(self.template_selector, stretch=1)
        template_row.addWidget(self.apply_template_button)
        template_row.addWidget(self.save_template_button)

        # --- Groupe : Informations client ---
        client_group = QGroupBox("Informations client")
        client_form = QFormLayout(client_group)
        self._new_client_label = "— Nouveau client —"
        self._client_contacts: dict[str, str] = {}
        self.client_selector = QComboBox()
        self.client_selector.addItem(self._new_client_label)
        self.client_name = QLineEdit()
        self.client_name.setPlaceholderText("Nom complet du client *")
        self.client_contact = QLineEdit()
        self.client_contact.setPlaceholderText("Téléphone ou e-mail")
        client_form.addRow("Client existant", self.client_selector)
        client_form.addRow("Nom du client *", self.client_name)
        client_form.addRow("Contact", self.client_contact)
        self.client_selector.currentIndexChanged.connect(self._on_client_selected)

        # --- Groupe : Caractéristiques du projet ---
        project_group = QGroupBox("Caractéristiques du projet")
        project_form = QFormLayout(project_group)

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Nom du projet")

        self.project_type = QComboBox()
        self.project_type.addItems(PROJECT_TYPES)

        self.location = QComboBox()
        self.location.addItems(LOCATIONS)

        self.surface_m2 = QDoubleSpinBox()
        self.surface_m2.setMinimum(0.0)
        self.surface_m2.setMaximum(100_000.0)
        self.surface_m2.setDecimals(1)
        self.surface_m2.setSuffix(" m²")
        self.surface_m2.setValue(0.0)

        self.length_m = QDoubleSpinBox()
        self.length_m.setMinimum(0.0)
        self.length_m.setMaximum(10_000.0)
        self.length_m.setDecimals(2)
        self.length_m.setSuffix(" m")
        self.length_m.setValue(0.0)

        self.width_m = QDoubleSpinBox()
        self.width_m.setMinimum(0.0)
        self.width_m.setMaximum(10_000.0)
        self.width_m.setDecimals(2)
        self.width_m.setSuffix(" m")
        self.width_m.setValue(0.0)

        self.height_m = QDoubleSpinBox()
        self.height_m.setMinimum(0.0)
        self.height_m.setMaximum(10_000.0)
        self.height_m.setDecimals(2)
        self.height_m.setSuffix(" m")
        self.height_m.setValue(0.0)

        self.thickness_m = QDoubleSpinBox()
        self.thickness_m.setMinimum(0.0)
        self.thickness_m.setMaximum(100.0)
        self.thickness_m.setDecimals(3)
        self.thickness_m.setSuffix(" m")
        self.thickness_m.setValue(0.0)

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

        project_form.addRow("Nom du projet", self.project_name)
        project_form.addRow("Type de projet *", self.project_type)
        project_form.addRow("Localisation *", self.location)
        project_form.addRow("Surface", self.surface_m2)
        project_form.addRow("Longueur", self.length_m)
        project_form.addRow("Largeur", self.width_m)
        project_form.addRow("Hauteur", self.height_m)
        project_form.addRow("Épaisseur", self.thickness_m)
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
        self.finish_level.setCurrentIndex(1)

        self.complexity = QComboBox()
        self.complexity.addItems(COMPLEXITY_LEVELS)
        self.complexity.setCurrentIndex(1)

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

        main_layout.addWidget(template_group)
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
        self.project_type.currentIndexChanged.connect(self._on_project_type_changed)
        self.apply_template_button.clicked.connect(self._on_apply_template_clicked)
        self.save_template_button.clicked.connect(self._on_save_template_clicked)

    def set_clients(self, clients: list[dict[str, object]]) -> None:
        """Alimente le sélecteur de clients existants."""
        current = self.client_selector.currentText()
        self.client_selector.blockSignals(True)
        self.client_selector.clear()
        self.client_selector.addItem(self._new_client_label)
        self._client_contacts = {}
        for client in clients:
            name = str(client["name"])
            self._client_contacts[name] = str(client.get("contact") or client.get("phone") or "")
            self.client_selector.addItem(name)
        index = self.client_selector.findText(current)
        self.client_selector.setCurrentIndex(index if index >= 0 else 0)
        self.client_selector.blockSignals(False)

    def _on_client_selected(self) -> None:
        name = self.client_selector.currentText()
        if name == self._new_client_label:
            return
        self.client_name.setText(name)
        self.client_contact.setText(self._client_contacts.get(name, ""))

    def _on_calculate(self) -> None:
        errors = self._validate()
        if errors:
            QMessageBox.warning(
                self,
                "Champs invalides",
                "Veuillez corriger les erreurs suivantes :\n\n" + "\n".join(f"\u2022 {e}" for e in errors),
            )
            return
        self.quote_requested.emit(self._build_input())

    def _validate(self) -> list[str]:
        errors: list[str] = []
        if not self.client_name.text().strip():
            errors.append("Le nom du client est obligatoire.")
        return errors

    def set_templates(self, templates: list[dict[str, object]]) -> None:
        current = self.template_selector.currentText()
        self.template_selector.blockSignals(True)
        self.template_selector.clear()
        self.template_selector.addItem(self._no_template_label)
        self._templates = {}
        for template in templates:
            name = str(template["name"])
            self._templates[name] = dict(template.get("payload") or {})
            self.template_selector.addItem(name)
        index = self.template_selector.findText(current)
        self.template_selector.setCurrentIndex(index if index >= 0 else 0)
        self.template_selector.blockSignals(False)

    def apply_template(self, payload: dict[str, object]) -> None:
        """Remplit les champs projet/technique depuis un modèle, sans laisser le
        pré-remplissage automatique du type écraser les valeurs du modèle."""
        self._applying_template = True
        try:
            _set_combo(self.project_type, str(payload.get("project_type", "")))
            self.surface_m2.setValue(float(payload.get("surface_m2", 0.0)))
            self.length_m.setValue(float(payload.get("length_m", 0.0)))
            self.width_m.setValue(float(payload.get("width_m", 0.0)))
            self.height_m.setValue(float(payload.get("height_m", 0.0)))
            self.thickness_m.setValue(float(payload.get("thickness_m", 0.0)))
            self.floors.setValue(int(payload.get("floors", 1)))
            self.room_count.setValue(int(payload.get("room_count", 0)))
            _set_combo(self.structure_type, str(payload.get("structure_type", "")))
            _set_combo(self.roof_type, str(payload.get("roof_type", "")))
            _set_combo(self.finish_level, str(payload.get("finish_level", "")))
            _set_combo(self.complexity, str(payload.get("complexity", "")))
            self.notes.setPlainText(str(payload.get("notes", "")))
        finally:
            self._applying_template = False

    def _on_apply_template_clicked(self) -> None:
        name = self.template_selector.currentText()
        payload = self._templates.get(name)
        if payload:
            self.apply_template(payload)

    def _on_save_template_clicked(self) -> None:
        name, ok = QInputDialog.getText(self, "Enregistrer le modèle", "Nom du modèle :")
        if ok and name.strip():
            self.save_template_requested.emit(name.strip(), self._build_input())

    def _on_project_type_changed(self) -> None:
        if self._applying_template:
            return
        ptype = self.project_type.currentText()
        if ptype == "Mur":
            self.length_m.setValue(10.0)
            self.height_m.setValue(2.5)
            self.thickness_m.setValue(0.2)
            self.width_m.setValue(0.0)
            self.surface_m2.setValue(0.0)
        elif ptype == "Dalle béton":
            self.length_m.setValue(5.0)
            self.width_m.setValue(4.0)
            self.thickness_m.setValue(0.15)
            self.surface_m2.setValue(0.0)
            self.height_m.setValue(0.0)
        elif ptype == "Route":
            self.thickness_m.setValue(0.15)
            self.surface_m2.setValue(500.0)
            self.length_m.setValue(0.0)
            self.width_m.setValue(0.0)
            self.height_m.setValue(0.0)
        elif ptype == "Maison":
            self.surface_m2.setValue(100.0)
            self.length_m.setValue(0.0)
            self.width_m.setValue(0.0)
            self.height_m.setValue(0.0)
            self.thickness_m.setValue(0.0)
        else:
            self.surface_m2.setValue(0.0)
            self.length_m.setValue(0.0)
            self.width_m.setValue(0.0)
            self.height_m.setValue(0.0)
            self.thickness_m.setValue(0.0)

    def _build_input(self) -> QuoteInput:
        return QuoteInput(
            client_name=self.client_name.text().strip(),
            client_contact=self.client_contact.text().strip(),
            project_name=self.project_name.text().strip(),
            project_type=self.project_type.currentText(),
            location=self.location.currentText(),
            surface_m2=self.surface_m2.value(),
            length_m=self.length_m.value(),
            width_m=self.width_m.value(),
            height_m=self.height_m.value(),
            thickness_m=self.thickness_m.value(),
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
        self.project_name.clear()
        self.project_type.setCurrentIndex(0)
        self.location.setCurrentIndex(0)
        self.surface_m2.setValue(0.0)
        self.length_m.setValue(0.0)
        self.width_m.setValue(0.0)
        self.height_m.setValue(0.0)
        self.thickness_m.setValue(0.0)
        self.floors.setValue(1)
        self.room_count.setValue(4)
        self.structure_type.setCurrentIndex(0)
        self.roof_type.setCurrentIndex(0)
        self.finish_level.setCurrentIndex(1)
        self.complexity.setCurrentIndex(1)
        self.notes.clear()

    def populate_from_input(self, quote_input: QuoteInput) -> None:
        self.client_name.setText(quote_input.client_name)
        self.client_contact.setText(quote_input.client_contact)
        self.project_name.setText(quote_input.project_name)
        _set_combo(self.project_type, quote_input.project_type)
        _set_combo(self.location, quote_input.location)
        self.surface_m2.setValue(quote_input.surface_m2)
        self.length_m.setValue(quote_input.length_m)
        self.width_m.setValue(quote_input.width_m)
        self.height_m.setValue(quote_input.height_m)
        self.thickness_m.setValue(quote_input.thickness_m)
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
