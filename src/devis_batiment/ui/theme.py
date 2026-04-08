"""Feuille de style globale — thème moderne pour Jeannot Devis Bâtiment."""
from __future__ import annotations

from pathlib import Path

_ICONS = Path(__file__).parent / "icons"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
PRIMARY       = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
PRIMARY_PRESS = "#1E40AF"
SUCCESS       = "#16A34A"
DANGER        = "#DC2626"
DANGER_HOVER  = "#B91C1C"

BG_APP        = "#F1F5F9"   # fond général
BG_SURFACE    = "#FFFFFF"   # cartes / groupes
BG_ALT        = "#F8FAFC"   # lignes alternées tableau
BG_HOVER      = "#EFF6FF"   # survol léger

BORDER        = "#CBD5E1"
BORDER_FOCUS  = "#93C5FD"

TEXT          = "#0F172A"
TEXT_MUTED    = "#64748B"
TEXT_WHITE    = "#FFFFFF"

RADIUS_SM     = "4px"
RADIUS        = "6px"
RADIUS_LG     = "8px"


def _stylesheet() -> str:
    arrow_down = (_ICONS / "arrow_down.svg").as_posix()
    arrow_up   = (_ICONS / "arrow_up.svg").as_posix()
    return f"""
/* ── Base ────────────────────────────────────────────────────────────────── */
QWidget {{
    font-family: "Segoe UI", "Noto Sans", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {TEXT};
    background-color: {BG_APP};
}}

QMainWindow {{
    background-color: {BG_APP};
}}

QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: transparent;
    border: none;
}}

/* ── Onglets ─────────────────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: {RADIUS_LG};
    background-color: {BG_SURFACE};
    margin-top: -1px;
}}

QTabBar::tab {{
    background-color: {BG_APP};
    color: {TEXT_MUTED};
    border: 1px solid {BORDER};
    border-bottom: none;
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: {RADIUS};
    border-top-right-radius: {RADIUS};
    font-weight: 500;
    min-width: 100px;
}}

QTabBar::tab:selected {{
    background-color: {BG_SURFACE};
    color: {PRIMARY};
    border-bottom: 2px solid {PRIMARY};
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background-color: {BG_HOVER};
    color: {TEXT};
}}

/* ── GroupBox ────────────────────────────────────────────────────────────── */
QGroupBox {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_LG};
    margin-top: 14px;
    padding: 12px 14px 10px 14px;
    font-weight: 600;
    font-size: 12px;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: -2px;
    padding: 0 6px;
    background-color: {BG_SURFACE};
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}

/* ── Champs de saisie ────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {BG_SURFACE};
    border: 1.5px solid {BORDER};
    border-radius: {RADIUS};
    padding: 5px 8px;
    color: {TEXT};
    selection-background-color: {BORDER_FOCUS};
}}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {PRIMARY};
    background-color: {BG_SURFACE};
    outline: none;
}}

QLineEdit:hover, QTextEdit:hover, QSpinBox:hover,
QDoubleSpinBox:hover, QComboBox:hover {{
    border-color: #94A3B8;
}}

QLineEdit::placeholder, QTextEdit::placeholder {{
    color: {TEXT_MUTED};
}}

/* ── ComboBox ────────────────────────────────────────────────────────────── */
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid {BORDER};
    border-top-right-radius: {RADIUS};
    border-bottom-right-radius: {RADIUS};
    background-color: transparent;
}}

QComboBox::down-arrow {{
    image: url({arrow_down});
    width: 10px;
    height: 6px;
}}

QComboBox QAbstractItemView {{
    border: 1px solid {BORDER};
    background-color: {BG_SURFACE};
    selection-background-color: {BG_HOVER};
    selection-color: {PRIMARY};
    padding: 4px;
    outline: none;
}}

/* ── SpinBox ─────────────────────────────────────────────────────────────── */
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid {BORDER};
    border-bottom: 1px solid {BORDER};
    border-top-right-radius: {RADIUS};
    background-color: transparent;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 18px;
    border-left: 1px solid {BORDER};
    border-bottom-right-radius: {RADIUS};
    background-color: transparent;
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url({arrow_up});
    width: 10px;
    height: 6px;
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url({arrow_down});
    width: 10px;
    height: 6px;
}}

/* ── Boutons ─────────────────────────────────────────────────────────────── */
QPushButton {{
    background-color: #E2E8F0;
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
    padding: 6px 16px;
    font-weight: 500;
    min-height: 30px;
}}

QPushButton:hover {{
    background-color: #CBD5E1;
    border-color: #94A3B8;
}}

QPushButton:pressed {{
    background-color: #94A3B8;
}}

QPushButton:disabled {{
    background-color: {BG_APP};
    color: #94A3B8;
    border-color: #E2E8F0;
}}

QPushButton[class="primary"] {{
    background-color: {PRIMARY};
    color: {TEXT_WHITE};
    border: none;
    font-weight: 600;
}}

QPushButton[class="primary"]:hover {{
    background-color: {PRIMARY_HOVER};
}}

QPushButton[class="primary"]:pressed {{
    background-color: {PRIMARY_PRESS};
}}

QPushButton[class="danger"] {{
    background-color: {BG_SURFACE};
    color: {DANGER};
    border-color: {DANGER};
}}

QPushButton[class="danger"]:hover {{
    background-color: {DANGER};
    color: {TEXT_WHITE};
}}

/* ── Tableaux ────────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {BG_SURFACE};
    alternate-background-color: {BG_ALT};
    gridline-color: #E2E8F0;
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
    selection-background-color: {BG_HOVER};
    selection-color: {TEXT};
    outline: none;
}}

QTableWidget::item {{
    padding: 5px 8px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: #DBEAFE;
    color: {TEXT};
}}

QHeaderView::section {{
    background-color: {BG_APP};
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 2px solid {BORDER};
    border-right: 1px solid {BORDER};
    padding: 6px 8px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}

QHeaderView::section:last {{
    border-right: none;
}}

/* ── Barre de défilement ─────────────────────────────────────────────────── */
QScrollBar:vertical {{
    width: 8px;
    background: transparent;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: #94A3B8;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    height: 8px;
    background: transparent;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #94A3B8;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── Étiquettes ──────────────────────────────────────────────────────────── */
QLabel {{
    background-color: transparent;
    color: {TEXT};
}}

/* ── Messages ────────────────────────────────────────────────────────────── */
QMessageBox {{
    background-color: {BG_SURFACE};
}}

QMessageBox QPushButton {{
    min-width: 80px;
}}

/* ── Formulaires ─────────────────────────────────────────────────────────── */
QFormLayout QLabel {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 500;
}}

/* ── Dialogues ───────────────────────────────────────────────────────────── */
QDialog {{
    background-color: {BG_SURFACE};
}}

QDialogButtonBox QPushButton {{
    min-width: 90px;
}}

/* ── Frame résultat devis ────────────────────────────────────────────────── */
QFrame#totalFrame {{
    background-color: #EFF6FF;
    border: 1.5px solid #BFDBFE;
    border-radius: {RADIUS_LG};
}}
"""


def apply(app) -> None:  # type: ignore[type-arg]
    """Applique le stylesheet global à l'application Qt."""
    app.setStyle("Fusion")
    app.setStyleSheet(_stylesheet())
