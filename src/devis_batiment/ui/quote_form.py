from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLineEdit, QSpinBox, QWidget


class QuoteFormWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.client_name = QLineEdit()
        self.surface_m2 = QLineEdit()
        self.floors = QSpinBox()
        self.floors.setMinimum(0)
        self.floors.setMaximum(50)
        layout.addRow("Client", self.client_name)
        layout.addRow("Surface (m2)", self.surface_m2)
        layout.addRow("Etages", self.floors)
