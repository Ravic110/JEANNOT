from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
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

from devis_batiment.services import SettingsService


class SettingsView(QWidget):
    def __init__(self, settings_service: SettingsService | None = None) -> None:
        super().__init__()
        self.settings_service = settings_service

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # --- Groupe : Informations de l'entreprise ---
        company_group = QGroupBox("Informations de l'entreprise")
        company_form = QFormLayout(company_group)

        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Nom de votre entreprise")

        self.company_address = QLineEdit()
        self.company_address.setPlaceholderText("Adresse complète")

        self.company_phone = QLineEdit()
        self.company_phone.setPlaceholderText("Ex : +261 20 ...")

        self.company_email = QLineEdit()
        self.company_email.setPlaceholderText("contact@entreprise.mg")

        self.company_logo = QLineEdit()
        self.company_logo.setPlaceholderText("Chemin vers le logo (ex: assets/logo.png)")
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.company_logo)
        logo_btn = QPushButton("...")
        logo_btn.setFixedWidth(36)
        logo_btn.clicked.connect(self._on_browse_logo)
        logo_layout.addWidget(logo_btn)

        company_form.addRow("Nom de l'entreprise", self.company_name)
        company_form.addRow("Adresse", self.company_address)
        company_form.addRow("Téléphone", self.company_phone)
        company_form.addRow("E-mail", self.company_email)
        company_form.addRow("Logo", logo_layout)

        # --- Groupe : Paramètres de calcul ---
        calc_group = QGroupBox("Paramètres de calcul")
        calc_form = QFormLayout(calc_group)

        self.safety_margin_pct = QDoubleSpinBox()
        self.safety_margin_pct.setMinimum(0.0)
        self.safety_margin_pct.setMaximum(50.0)
        self.safety_margin_pct.setDecimals(1)
        self.safety_margin_pct.setSingleStep(0.5)
        self.safety_margin_pct.setSuffix(" %")
        self.safety_margin_pct.setToolTip(
            "Pourcentage ajouté au montant final pour couvrir les imprévus."
        )

        self.currency = QLineEdit()
        self.currency.setPlaceholderText("Ex : Ar, MGA, €")
        self.currency.setMaximumWidth(80)

        self.quote_validity_days = QSpinBox()
        self.quote_validity_days.setMinimum(1)
        self.quote_validity_days.setMaximum(365)
        self.quote_validity_days.setSuffix(" jour(s)")

        calc_form.addRow("Marge de sécurité", self.safety_margin_pct)
        calc_form.addRow("Devise affichée", self.currency)
        calc_form.addRow("Validité du devis", self.quote_validity_days)

        # --- Groupe : Facturation & mentions ---
        billing_group = QGroupBox("Facturation & mentions")
        billing_form = QFormLayout(billing_group)

        self.vat_enabled = QCheckBox("Appliquer la TVA sur le devis")
        self.vat_enabled.setToolTip(
            "Décochez si vous n'êtes pas assujetti : le devis affichera "
            "« TVA non applicable »."
        )

        self.vat_rate_pct = QDoubleSpinBox()
        self.vat_rate_pct.setMinimum(0.0)
        self.vat_rate_pct.setMaximum(100.0)
        self.vat_rate_pct.setDecimals(1)
        self.vat_rate_pct.setSingleStep(0.5)
        self.vat_rate_pct.setSuffix(" %")

        self.deposit_pct = QDoubleSpinBox()
        self.deposit_pct.setMinimum(0.0)
        self.deposit_pct.setMaximum(100.0)
        self.deposit_pct.setDecimals(1)
        self.deposit_pct.setSingleStep(5.0)
        self.deposit_pct.setSuffix(" %")
        self.deposit_pct.setToolTip("Acompte demandé à la commande (0 = aucun).")

        self.payment_terms = QTextEdit()
        self.payment_terms.setPlaceholderText(
            "Ex : Acompte de 30 % à la commande, solde à la livraison."
        )
        self.payment_terms.setMaximumHeight(70)

        self.terms_conditions = QTextEdit()
        self.terms_conditions.setPlaceholderText(
            "Conditions générales / clause de réserve affichées en bas du devis."
        )
        self.terms_conditions.setMaximumHeight(70)

        billing_form.addRow("TVA", self.vat_enabled)
        billing_form.addRow("Taux de TVA", self.vat_rate_pct)
        billing_form.addRow("Acompte à la commande", self.deposit_pct)
        billing_form.addRow("Conditions de règlement", self.payment_terms)
        billing_form.addRow("Conditions générales", self.terms_conditions)

        # --- Boutons ---
        btn_layout = QHBoxLayout()
        self._status_label = QLabel()
        self._status_label.setStyleSheet("color: #16A34A; font-weight: 500;")
        self.save_button = QPushButton("Enregistrer les paramètres")
        self.save_button.setMinimumHeight(36)
        self.save_button.setProperty("class", "primary")
        btn_layout.addWidget(self._status_label)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_button)

        main_layout.addWidget(company_group)
        main_layout.addWidget(calc_group)
        main_layout.addWidget(billing_group)
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

        self.save_button.clicked.connect(self._on_save)

    def set_service(self, settings_service: SettingsService) -> None:
        self.settings_service = settings_service
        self.load()

    def load(self) -> None:
        if self.settings_service is None:
            return
        values = self.settings_service.get_all()
        self.company_name.setText(values.get("company_name", ""))
        self.company_address.setText(values.get("company_address", ""))
        self.company_phone.setText(values.get("company_phone", ""))
        self.company_email.setText(values.get("company_email", ""))
        self.company_logo.setText(values.get("company_logo", ""))
        self.currency.setText(values.get("currency", "Ar"))
        try:
            self.safety_margin_pct.setValue(float(values.get("safety_margin_pct", "0")))
        except ValueError:
            self.safety_margin_pct.setValue(0.0)
        try:
            self.quote_validity_days.setValue(int(values.get("quote_validity_days", "30")))
        except ValueError:
            self.quote_validity_days.setValue(30)
        self.vat_enabled.setChecked(values.get("vat_enabled", "false") == "true")
        try:
            self.vat_rate_pct.setValue(float(values.get("vat_rate_pct", "20")))
        except ValueError:
            self.vat_rate_pct.setValue(20.0)
        try:
            self.deposit_pct.setValue(float(values.get("deposit_pct", "0")))
        except ValueError:
            self.deposit_pct.setValue(0.0)
        self.payment_terms.setPlainText(values.get("payment_terms", ""))
        self.terms_conditions.setPlainText(values.get("terms_conditions", ""))
        self._status_label.setText("")

    def _on_browse_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le logo", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self.company_logo.setText(path)

    def _on_save(self) -> None:
        if self.settings_service is None:
            return
        try:
            self.settings_service.save_all({
                "company_name": self.company_name.text().strip(),
                "company_address": self.company_address.text().strip(),
                "company_phone": self.company_phone.text().strip(),
                "company_email": self.company_email.text().strip(),
                "company_logo": self.company_logo.text().strip(),
                "currency": self.currency.text().strip() or "Ar",
                "safety_margin_pct": str(self.safety_margin_pct.value()),
                "quote_validity_days": str(self.quote_validity_days.value()),
                "vat_enabled": "true" if self.vat_enabled.isChecked() else "false",
                "vat_rate_pct": str(self.vat_rate_pct.value()),
                "deposit_pct": str(self.deposit_pct.value()),
                "payment_terms": self.payment_terms.toPlainText().strip(),
                "terms_conditions": self.terms_conditions.toPlainText().strip(),
            })
            self._status_label.setText("Paramètres enregistrés.")
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer :\n{exc}")
