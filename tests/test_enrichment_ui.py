from pathlib import Path

from PySide6.QtWidgets import QApplication

from devis_batiment.models import QuoteInput
from devis_batiment.services import AdminService, ClientService, QuoteWorkflow
from devis_batiment.storage import Database


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _seed_materials(database: Database) -> None:
    admin = AdminService(database)
    for name, unit, price in [
        ("Ciment", "sacs 50kg", 45_000),
        ("Sable", "m³", 180_000),
        ("Gravier", "m³", 190_000),
        ("Fer", "kg", 4_000),
        ("Main d'œuvre", "jour", 220_000),
    ]:
        admin.save_material(name, unit, price)
    admin.save_breakdown_rule("Matériaux", 0.8)
    admin.save_breakdown_rule("Main d'œuvre", 0.2)


def _make_input(name: str = "M. Rakoto") -> QuoteInput:
    return QuoteInput(
        client_name=name, client_contact="0330000000", project_name="Villa",
        project_type="Maison", location="Antananarivo", surface_m2=100.0,
        length_m=0.0, width_m=0.0, height_m=0.0, thickness_m=0.0, floors=1,
        structure_type="Béton armé", roof_type="Tôle", room_count=4,
        finish_level="Standard", complexity="Simple",
    )


# --- Lot B UI : statut dans l'historique + dashboard ---


def test_history_view_has_status_column(qtbot):
    _app()
    from devis_batiment.ui.history_view import HistoryView

    view = HistoryView()
    qtbot.addWidget(view)

    assert view.quote_table.columnCount() == 5
    headers = [
        view.quote_table.horizontalHeaderItem(i).text()
        for i in range(view.quote_table.columnCount())
    ]
    assert "Statut" in headers


def test_history_view_apply_status_updates_db(qtbot):
    _app()
    from devis_batiment.services import QuoteService
    from devis_batiment.ui.history_view import HistoryView

    database = Database(Path(":memory:"))
    database.initialize()
    _seed_materials(database)
    quote_id, _ = QuoteWorkflow(database).create_quote(_make_input())

    view = HistoryView(QuoteService(database))
    qtbot.addWidget(view)

    view.apply_status(quote_id, "Accepté")

    assert database.fetch_quotes()[0]["status"] == "Accepté"


def test_transformation_rate_excludes_drafts():
    from devis_batiment.ui.dashboard_view import compute_transformation_rate

    counts = {"Brouillon": 5, "Envoyé": 1, "Accepté": 2, "Refusé": 1}
    assert compute_transformation_rate(counts) == 0.5


def test_transformation_rate_zero_when_no_sent_quotes():
    from devis_batiment.ui.dashboard_view import compute_transformation_rate

    assert compute_transformation_rate({"Brouillon": 3}) == 0.0


# --- Lot A UI : fiches clients enrichies + sélecteur dans le formulaire ---


def test_client_dialog_collects_enriched_fields(qtbot):
    _app()
    from devis_batiment.ui.clients_view import _ClientDialog

    dialog = _ClientDialog()
    qtbot.addWidget(dialog)
    dialog.name.setText("SARL Betonline")
    dialog.client_type.setCurrentText("Entreprise")
    dialog.email.setText("contact@betonline.mg")
    dialog.phone.setText("0340000000")
    dialog.address.setText("Lot II")
    dialog.site_address.setText("Ivandry")
    dialog.notes.setText("VIP")

    values = dialog.values()

    assert values["name"] == "SARL Betonline"
    assert values["client_type"] == "Entreprise"
    assert values["email"] == "contact@betonline.mg"
    assert values["phone"] == "0340000000"
    assert values["address"] == "Lot II"
    assert values["site_address"] == "Ivandry"
    assert values["notes"] == "VIP"


def test_clients_view_filters_by_type(qtbot):
    _app()
    from devis_batiment.ui.clients_view import ClientsView

    database = Database(Path(":memory:"))
    database.initialize()
    service = ClientService(database)
    service.save_client("M. Rakoto", client_type="Particulier")
    service.save_client("SARL Betonline", client_type="Entreprise")

    view = ClientsView(service)
    qtbot.addWidget(view)
    view.type_filter.setCurrentText("Entreprise")
    view.refresh()

    names = [
        view.table.item(r, 1).text() for r in range(view.table.rowCount())
    ]
    assert names == ["SARL Betonline"]


def test_clients_view_shows_client_quotes(qtbot):
    _app()
    from devis_batiment.ui.clients_view import ClientsView

    database = Database(Path(":memory:"))
    database.initialize()
    _seed_materials(database)
    QuoteWorkflow(database).create_quote(_make_input("Mme Ranaivo"))
    service = ClientService(database)
    client_id = service.list_clients()[0]["id"]

    view = ClientsView(service)
    qtbot.addWidget(view)
    view.show_client_quotes(client_id)

    assert view.quotes_table.rowCount() == 1


def test_quote_form_client_selector_prefills_name(qtbot):
    _app()
    from devis_batiment.ui.quote_form import QuoteFormWidget

    form = QuoteFormWidget()
    qtbot.addWidget(form)
    form.set_clients(
        [{"name": "M. Rakoto", "contact": "0331234567", "client_type": "Particulier"}]
    )

    form.client_selector.setCurrentText("M. Rakoto")

    assert form.client_name.text() == "M. Rakoto"
    assert form.client_contact.text() == "0331234567"


# --- Lot C UI : modèles dans le formulaire ---


def test_quote_form_set_templates_populates_selector(qtbot):
    _app()
    from devis_batiment.ui.quote_form import QuoteFormWidget

    form = QuoteFormWidget()
    qtbot.addWidget(form)
    form.set_templates([{"name": "Maison standard", "payload": {}}])

    items = [
        form.template_selector.itemText(i)
        for i in range(form.template_selector.count())
    ]
    assert "Maison standard" in items


def test_quote_form_apply_template_survives_type_prefill(qtbot):
    _app()
    from devis_batiment.ui.quote_form import QuoteFormWidget

    form = QuoteFormWidget()
    qtbot.addWidget(form)

    # Un modèle « Mur » avec des dimensions volontairement différentes du
    # pré-remplissage automatique du type (qui, pour un Mur, mettrait
    # length=10 et surface=0).
    payload = {
        "project_type": "Mur",
        "surface_m2": 42.0,
        "length_m": 7.0,
        "width_m": 0.0,
        "height_m": 2.5,
        "thickness_m": 0.2,
        "floors": 1,
        "room_count": 0,
        "structure_type": "Béton armé",
        "roof_type": "Tôle",
        "finish_level": "Standard",
        "complexity": "Moyenne",
        "notes": "Modèle mur",
    }
    form.apply_template(payload)

    assert form.project_type.currentText() == "Mur"
    assert form.length_m.value() == 7.0
    assert form.surface_m2.value() == 42.0
    assert form.structure_type.currentText() == "Béton armé"
    assert form.notes.toPlainText() == "Modèle mur"
