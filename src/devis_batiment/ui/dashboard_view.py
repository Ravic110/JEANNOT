from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from devis_batiment.storage import Database
from devis_batiment.ui.formatting import format_amount


def compute_transformation_rate(counts: dict[str, int]) -> float:
    """Taux de transformation = Accepté / (Envoyé + Accepté + Refusé).

    Les brouillons sont exclus ; renvoie 0.0 si aucun devis n'a quitté l'état
    brouillon.
    """
    accepted = counts.get("Accepté", 0)
    considered = accepted + counts.get("Envoyé", 0) + counts.get("Refusé", 0)
    if considered == 0:
        return 0.0
    return accepted / considered


class DashboardView(QWidget):
    def __init__(self, database: Database | None = None) -> None:
        super().__init__()
        self.database = database
        self._currency = "Ar"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        summary = QHBoxLayout()
        summary.setSpacing(12)

        self.quotes_label = self._build_card("Devis enregistrés")
        self.revenue_label = self._build_card("CA estimé")
        self.accepted_revenue_label = self._build_card("CA accepté")
        self.transformation_label = self._build_card("Taux de transformation")
        self.projects_label = self._build_card("Projets actifs")

        summary.addWidget(self.quotes_label)
        summary.addWidget(self.revenue_label)
        summary.addWidget(self.accepted_revenue_label)
        summary.addWidget(self.transformation_label)
        summary.addWidget(self.projects_label)

        recent_group = QGroupBox("Devis récents")
        recent_layout = QVBoxLayout(recent_group)
        self.recent_table = QTableWidget(0, 4)
        self.recent_table.setHorizontalHeaderLabels(["N°", "Client", "Date", "Montant"])
        self.recent_table.horizontalHeader().setStretchLastSection(True)
        self.recent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recent_table.setAlternatingRowColors(True)
        recent_layout.addWidget(self.recent_table)

        layout.addLayout(summary)
        layout.addWidget(recent_group)
        layout.addStretch()

    def _build_card(self, title: str) -> QLabel:
        label = QLabel(f"<b>{title}</b><br>–")
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setMinimumHeight(86)
        label.setStyleSheet(
            "background:#FFFFFF; border:1px solid #D1D5DB; border-radius:10px; padding:14px;"
        )
        return label

    def set_currency(self, currency: str) -> None:
        self._currency = currency or "Ar"

    def refresh(self) -> None:
        if self.database is None:
            return
        total_quotes = self.database.count_quotes()
        total_revenue = self.database.sum_quote_amounts()
        total_projects = self.database.count_projects()

        counts = self.database.count_quotes_by_status()
        accepted_revenue = self.database.sum_amount_by_status("Accepté")
        rate = compute_transformation_rate(counts)

        self.quotes_label.setText(f"<b>Devis enregistrés</b><br>{total_quotes}")
        self.revenue_label.setText(f"<b>CA estimé</b><br>{format_amount(total_revenue, self._currency)}")
        self.accepted_revenue_label.setText(
            f"<b>CA accepté</b><br>{format_amount(accepted_revenue, self._currency)}"
        )
        self.transformation_label.setText(
            f"<b>Taux de transformation</b><br>{rate * 100:.0f} %"
        )
        self.projects_label.setText(f"<b>Projets actifs</b><br>{total_projects}")

        recent = self.database.fetch_recent_quotes(5)
        self.recent_table.setRowCount(len(recent))
        for i, row in enumerate(recent):
            self.recent_table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.recent_table.setItem(i, 1, QTableWidgetItem(str(row["client_name"])))
            date_str = str(row["created_at"])[:19].replace("T", " ")
            self.recent_table.setItem(i, 2, QTableWidgetItem(date_str))
            self.recent_table.setItem(i, 3, QTableWidgetItem(format_amount(float(row["total_amount"]), self._currency)))
        self.recent_table.resizeColumnsToContents()
