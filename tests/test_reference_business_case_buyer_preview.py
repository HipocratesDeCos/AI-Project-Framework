"""The buyer walkthrough remains a verified, inert fixture projection."""
import json

import pytest

from examples.reference_business_case_demo import create_reference_demo
from examples.reference_business_case_buyer_preview import render_buyer_preview


def test_full_preview_shows_both_variants_without_operational_actions(tmp_path):
    directory = tmp_path / "demo"
    create_reference_demo(
        directory, with_price=True, with_tco=True, with_supplier_risk=True,
        with_c0=True, with_decision_twin=True, with_scenario_coordination=True,
        with_negotiation_intelligence=True, with_negotiation_ladder=True,
    )
    html = render_buyer_preview(directory)
    assert html == render_buyer_preview(directory)
    assert html.count("Huella terminal:") == 2
    assert html.count("Calidad QTG:") == 2
    assert "NO_APTO / BAJA" in html and "APTO / ALTA" in html
    assert "DEMOSTRACIÓN SINTÉTICA — NO OPERACIONAL" in html
    assert "AUTHORIZED en una captura negociadora no constituye mandato" in html
    for label in ("Precio observado", "Coste de adquisición modelado", "Riesgo y valor",
                  "Evaluación C0", "Comparación de alternativas", "Coordinación de escenarios",
                  "Contenido de negociación", "Secuencia de negociación"):
        assert html.count(label) == 2
    for forbidden in ("<script", "<form", "<a ", "<iframe", "<button"):
        assert forbidden not in html


def test_preview_fails_closed_on_tampered_or_incomplete_bundle(tmp_path):
    directory = tmp_path / "demo"
    create_reference_demo(directory, with_price=True)
    (directory / "reference-price.json").unlink()
    with pytest.raises(ValueError, match="Both PRICE observations"):
        render_buyer_preview(directory)


def test_preview_fails_on_changed_terminal_and_handles_missing_optional_observations(tmp_path):
    directory = tmp_path / "demo"
    create_reference_demo(directory)
    html = render_buyer_preview(directory)
    assert html.count("No se exportaron observaciones adicionales") == 2
    terminal = directory / "reference-result.json"
    payload = json.loads(terminal.read_text(encoding="utf-8"))
    payload["operational_path"] = "ALLOWED"
    terminal.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        render_buyer_preview(directory)
