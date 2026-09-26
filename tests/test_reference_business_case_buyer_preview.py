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
    assert html.count("Propuesta ficticia común") == 1
    assert "ARTICLE-MOCK-001" in html and "SUPPLIER-MOCK-001" in html
    assert "20.50 EUR" in html and "10 unidades" in html
    assert "El precio unitario es un dato de entrada" in html
    assert "no evaluable" in html and "no satisfecho" in html
    assert "DEMOSTRACIÓN SINTÉTICA — NO OPERACIONAL" in html
    assert "AUTHORIZED en una captura negociadora no constituye mandato" in html
    assert html.count("Precio de referencia observado: <strong>20.25 EUR</strong>") == 2
    assert html.count("no es un precio objetivo, un techo autorizado") == 2
    assert html.count("Coste de adquisición modelado: <strong>205.00 EUR</strong>") == 2
    assert html.count("Lo no informado no equivale a coste cero") == 2
    assert html.count("Componentes incluidos: ACQUISITION") == 2
    assert html.count("Dimensiones de riesgo declaradas: RELIABILITY: FAVORABLE") == 2
    assert html.count("Fuentes factuales incluidas en este fixture: 0") == 2
    assert html.count("Comparación de valor disponible: no") == 2
    assert html.count("Base sintética suministrada: COMPRAR") == 2
    assert html.count("Consolidado CRC del fixture: <strong>COMPRAR</strong>") == 2
    assert "QTG de esta variante: NO_APTO" in html
    assert "QTG de esta variante: APTO" in html
    assert html.count("No se ha demostrado una derivación causal de QTG hacia C0") == 2
    assert html.count("Viabilidad declarada por Stage 2:") == 2
    assert html.count("ALT-1: VIABLE, REF-BUSINESS-001-ALT-2: VIABLE") == 2
    assert html.count("Diferencias en atributos incluidos: ninguna") == 2
    assert html.count("VIABLE no acredita viabilidad económica empresarial") == 2
    assert html.count("Escenarios descritos: 2") == 2
    assert html.count("La diferencia estructural en viability_result") == 2
    assert html.count("no selecciona ni prioriza un escenario") == 2
    assert html.count("Solicitud inicial declarada: Request a revised written quotation") == 2
    assert html.count("Alternativa de espera: Retain the simulated offer") == 2
    assert html.count("Justificaciones declaradas: 0") == 2
    assert html.count("AUTHORIZED pertenece al fixture sintético") == 2
    assert html.count("no demuestra que el texto se haya derivado causalmente de C0") == 2
    assert html.count("Pasos representados: 3; transiciones: 2; rutas: 1") == 2
    assert html.count("Posición 1: OBJECTIVE") == 2
    assert html.count("Posición 2: OPENING_REQUEST") == 2
    assert html.count("Posición 3: FALLBACK") == 2
    assert html.count("no prueba que el invocador NI separado haya producido el mismo objeto") == 2
    for label in ("Precio observado", "Coste de adquisición modelado", "Riesgo y valor",
                  "Evaluación C0", "Comparación de alternativas", "Coordinación de escenarios",
                  "Contenido de negociación", "Secuencia de negociación"):
        assert html.count(f"<h4>{label}") == 2
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


def test_demo_option_exports_and_replays_buyer_preview(tmp_path):
    from examples.reference_business_case_demo import verify_reference_demo

    directory = tmp_path / "demo"
    files = create_reference_demo(directory, with_price=True, with_buyer_preview=True)
    preview = directory / "reference-buyer-preview.html"
    assert files[-1] == preview
    assert preview.read_text(encoding="utf-8") == render_buyer_preview(directory)
    assert len(verify_reference_demo(directory)) == 2

    preview.write_text("<html>stale</html>", encoding="utf-8")
    with pytest.raises(ValueError, match="Buyer preview HTML differs"):
        verify_reference_demo(directory)


def test_demo_option_without_observations_is_valid(tmp_path):
    from examples.reference_business_case_demo import verify_reference_demo

    directory = tmp_path / "demo"
    files = create_reference_demo(directory, with_buyer_preview=True)
    assert len(files) == 4
    assert len(verify_reference_demo(directory)) == 2


def test_integrated_preview_verification_detects_changed_proposal_markup(tmp_path):
    from examples.reference_business_case_demo import verify_reference_demo

    directory = tmp_path / "demo"
    create_reference_demo(directory, with_buyer_preview=True)
    preview = directory / "reference-buyer-preview.html"
    preview.write_text(preview.read_text(encoding="utf-8").replace("20.50 EUR", "0.01 EUR"),
                       encoding="utf-8")
    with pytest.raises(ValueError, match="Buyer preview HTML differs"):
        verify_reference_demo(directory)
