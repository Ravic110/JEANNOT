from PySide6.QtWidgets import QApplication

from devis_batiment.config import PROJECT_TYPES
from devis_batiment.models import QuoteInput
from devis_batiment.ui.quote_form import QuoteFormWidget


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_quote_form_builds_valid_input(qtbot):
    app = _app()
    form = QuoteFormWidget()
    qtbot.addWidget(form)

    form.client_name.setText("Jean Dupont")
    form.client_contact.setText("0341234567")
    form.project_name.setText("Projet test")
    form.project_type.setCurrentText("Mur")
    form.location.setCurrentText("Antananarivo")
    form.length_m.setValue(12.0)
    form.width_m.setValue(0.5)
    form.height_m.setValue(3.0)
    form.thickness_m.setValue(0.25)
    form.floors.setValue(2)
    form.room_count.setValue(6)
    form.structure_type.setCurrentText("Béton armé")
    form.roof_type.setCurrentText("Tuile")
    form.finish_level.setCurrentText("Standard")
    form.complexity.setCurrentText("Moyenne")
    form.notes.setPlainText("Note de test")

    result = form._build_input()

    assert isinstance(result, QuoteInput)
    assert result.client_name == "Jean Dupont"
    assert result.client_contact == "0341234567"
    assert result.project_name == "Projet test"
    assert result.project_type == "Mur"
    assert result.project_type in PROJECT_TYPES
    assert result.location == "Antananarivo"
    assert result.length_m == 12.0
    assert result.width_m == 0.5
    assert result.height_m == 3.0
    assert result.thickness_m == 0.25
    assert result.floors == 2
    assert result.room_count == 6
    assert result.structure_type == "Béton armé"
    assert result.roof_type == "Tuile"
    assert result.finish_level == "Standard"
    assert result.complexity == "Moyenne"
    assert result.notes == "Note de test"


def test_quote_form_validation_rejects_empty_client(qtbot):
    app = _app()
    form = QuoteFormWidget()
    qtbot.addWidget(form)

    errors = form._validate()

    assert isinstance(errors, list)
    assert len(errors) > 0
    assert any("nom du client" in e.lower() for e in errors)
