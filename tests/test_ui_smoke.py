from PySide6.QtWidgets import QApplication

from devis_batiment.ui.main_window import MainWindow


def test_main_window_contains_core_tabs(qtbot):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    qtbot.addWidget(window)

    labels = [window.tabs.tabText(index) for index in range(window.tabs.count())]
    assert labels == ["Nouveau devis", "Resultat", "Historique", "Administration"]
