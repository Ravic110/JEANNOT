from devis_batiment.app import build_app_metadata


def test_build_app_metadata_returns_expected_defaults():
    metadata = build_app_metadata()

    assert metadata["app_name"] == "Jeannot Devis Batiment"
    assert metadata["database_name"] == "devis_batiment.db"
    assert metadata["currency"] == "MGA"
