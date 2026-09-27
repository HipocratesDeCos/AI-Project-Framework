"""Case 002 exports one same-run, replayable synthetic terminal and observations."""
import json
import sys

import pytest

from examples.reference_business_case_002 import (
    OBSERVATIONS, create_reference_business_case_002,
    execute_reference_business_case_002, main, verify_reference_business_case_002,
)


def test_second_runner_preserves_partial_result_and_same_run_sidecars():
    terminal, sidecars = execute_reference_business_case_002()
    replay, replay_sidecars = execute_reference_business_case_002()
    assert (terminal, sidecars) == (replay, replay_sidecars)
    assert terminal["reference_case_id"] == "REF-BUSINESS-002"
    assert terminal["capability_sequence"] == [
        "QTG", "PRICE", "TCO", "SUPPLIER_RISK_VALUE", "C0",
        "DECISION_TWIN", "SCENARIO_COORDINATION",
        "NEGOTIATION_INTELLIGENCE", "NEGOTIATION_LADDER",
    ]
    assert terminal["qtg_quality_result"]["status"] == "APTO"
    assert terminal["execution_outcome"]["status"] == "PARTIALLY_COMPLETED"
    assert terminal["execution_outcome"]["unresolved_items"] == [
        "RISK:SUPPLIER-MOCK-002:RELIABILITY:NOT_DETERMINABLE",
    ]
    assert terminal["case_provenance"]["material_nature"] == "SYNTHETIC"
    assert terminal["case_provenance"]["qtg_mode_policy"] == "SYNTHETIC_TEST_ONLY"
    assert terminal["case_provenance"]["effect_scope"] == "NO_OPERATIONAL_EFFECT"
    assert terminal["operational_path"] == "FORBIDDEN"
    assert terminal["operational_effect"] is False
    assert terminal["decision_authority"] is False
    assert set(sidecars) == set(OBSERVATIONS)
    assert sidecars["c0"]["crc_result"]["consolidated_result"] == "INFORMACIÓN INSUFICIENTE"
    assert sidecars["c0"]["qtg_c0_derivation_proven"] is False
    assert sidecars["supplier-risk"]["supplier_result"]["risk_dimensions"][0]["state"] == "NOT_DETERMINABLE"
    assert sidecars["decision-twin"]["selected_alternative"] is None
    for name, (_, validate, _) in OBSERVATIONS.items():
        assert sidecars[name]["terminal_fingerprint"] == terminal["terminal_fingerprint"]
        validate(sidecars[name], terminal)


def test_second_runner_export_replays_and_rejects_tampering(tmp_path):
    directory = tmp_path / "reference-002"
    paths = create_reference_business_case_002(directory)
    assert len(paths) == 9
    assert verify_reference_business_case_002(directory) == json.loads(
        (directory / "reference-result.json").read_text(encoding="utf-8")
    )["terminal_fingerprint"]
    with pytest.raises(FileExistsError):
        create_reference_business_case_002(directory)
    target = directory / "reference-c0.json"
    changed = json.loads(target.read_text(encoding="utf-8"))
    changed["crc_result"]["consolidated_result"] = "COMPRAR"
    target.write_text(json.dumps(changed, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    with pytest.raises(ValueError, match="reference-c0.json"):
        verify_reference_business_case_002(directory)


def test_second_runner_cli_explains_partial_status_and_forbidden_path(tmp_path, monkeypatch, capsys):
    directory = tmp_path / "reference-002-cli"
    monkeypatch.setattr(sys, "argv", ["reference_business_case_002", "--output-dir", str(directory)])
    main()
    output = capsys.readouterr().out
    assert "ejecución completada parcialmente (PARTIALLY_COMPLETED)" in output
    assert "ruta operacional prohibida (FORBIDDEN); sin autoridad decisional" in output
    assert verify_reference_business_case_002(directory)


def test_second_runner_review_is_read_only_and_replay_verified(tmp_path):
    directory = tmp_path / "reference-002-review"
    paths = create_reference_business_case_002(directory, with_review=True)
    assert len(paths) == 10
    html = (directory / "reference-review.html").read_text(encoding="utf-8")
    assert "Completada parcialmente" in html
    assert "Apta para esta prueba · Confianza alta" in html
    assert "sus nueve capacidades" in html
    assert "solicitar información documentada sobre la fiabilidad del proveedor" in html
    assert "Ask for documented supplier reliability information" not in html
    assert "Huella del resultado:" in html
    assert "no acredita la autenticidad de los documentos" in html
    assert "INFORMACIÓN INSUFICIENTE" in html
    assert "No determinable" in html
    assert "Datos ficticios · Solo para pruebas · Ruta operacional prohibida" in html
    assert "Sin efecto operacional · Sin autoridad para decidir" in html
    assert "Ver códigos técnicos de esta restricción" in html
    assert "SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false" in html
    assert "FORBIDDEN" in html
    assert "no se ha demostrado el vínculo" in html
    assert "<script" not in html.lower()
    assert verify_reference_business_case_002(directory)
    (directory / "reference-review.html").write_text(
        html.replace("Sin decisión de compra.", "Compra autorizada."), encoding="utf-8",
    )
    with pytest.raises(ValueError, match="reference-review.html"):
        verify_reference_business_case_002(directory)
