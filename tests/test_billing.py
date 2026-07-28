from pathlib import Path

from devis_batiment.services import SettingsService
from devis_batiment.services.billing import compute_totals
from devis_batiment.storage import Database


def test_no_vat_returns_base_as_total():
    totals = compute_totals(1_000_000.0, vat_enabled=False, vat_rate_pct=20.0, deposit_pct=0.0)

    assert totals.vat_enabled is False
    assert totals.total_ht == 1_000_000.0
    assert totals.vat_amount == 0.0
    assert totals.total_ttc == 1_000_000.0
    assert totals.deposit_amount == 0.0


def test_vat_20_percent_adds_tax():
    totals = compute_totals(1_000_000.0, vat_enabled=True, vat_rate_pct=20.0, deposit_pct=0.0)

    assert totals.total_ht == 1_000_000.0
    assert totals.vat_amount == 200_000.0
    assert totals.total_ttc == 1_200_000.0


def test_deposit_is_computed_on_ttc():
    totals = compute_totals(1_000_000.0, vat_enabled=True, vat_rate_pct=20.0, deposit_pct=30.0)

    # Acompte de 30 % du TTC (1 200 000)
    assert totals.total_ttc == 1_200_000.0
    assert totals.deposit_amount == 360_000.0


def test_deposit_without_vat_is_on_base():
    totals = compute_totals(1_000_000.0, vat_enabled=False, vat_rate_pct=20.0, deposit_pct=50.0)

    assert totals.total_ttc == 1_000_000.0
    assert totals.deposit_amount == 500_000.0


def test_zero_vat_rate_enabled_adds_nothing():
    totals = compute_totals(1_000_000.0, vat_enabled=True, vat_rate_pct=0.0, deposit_pct=0.0)

    assert totals.vat_amount == 0.0
    assert totals.total_ttc == 1_000_000.0


def test_settings_service_persists_billing_keys(tmp_path: Path):
    database = Database(tmp_path / "settings.db")
    database.initialize()
    service = SettingsService(database)

    service.save_all(
        {
            "vat_enabled": "true",
            "vat_rate_pct": "20",
            "deposit_pct": "30",
            "payment_terms": "Acompte à la commande, solde à la livraison.",
            "terms_conditions": "Devis valable sous réserve de disponibilité.",
        }
    )

    values = service.get_all()
    assert values["vat_enabled"] == "true"
    assert values["vat_rate_pct"] == "20"
    assert values["deposit_pct"] == "30"
    assert values["payment_terms"].startswith("Acompte")
    assert values["terms_conditions"].startswith("Devis valable")


def test_billing_keys_have_defaults(tmp_path: Path):
    database = Database(tmp_path / "settings.db")
    database.initialize()
    service = SettingsService(database)

    values = service.get_all()
    assert values["vat_enabled"] == "false"
    assert values["deposit_pct"] == "0"


def test_billing_lines_without_vat_show_single_total():
    from devis_batiment.utils.pdf import build_billing_lines

    lines = build_billing_lines(
        {"currency": "Ar", "vat_enabled": "false", "deposit_pct": "0"},
        1_000_000.0,
    )
    labels = [label for label, _ in lines]
    assert labels == ["Total"]


def test_billing_lines_with_vat_and_deposit():
    from devis_batiment.utils.pdf import build_billing_lines

    lines = build_billing_lines(
        {"currency": "Ar", "vat_enabled": "true", "vat_rate_pct": "20", "deposit_pct": "30"},
        1_000_000.0,
    )
    labels = [label for label, _ in lines]
    assert labels[0] == "Total HT"
    assert any("TVA" in label for label in labels)
    assert "Total TTC" in labels
    assert any("Acompte" in label for label in labels)
    # Le TTC formaté doit apparaître dans les valeurs.
    values = " ".join(value for _, value in lines)
    assert "1 200 000" in values
