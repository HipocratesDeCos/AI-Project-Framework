"""Single-command synthetic demonstration packaging."""
import json

import pytest

from examples.reference_business_case_demo import (
    create_reference_demo, verify_reference_demo,
)


def test_demo_generates_both_exact_terminal_results_and_review(tmp_path):
    output = tmp_path / "reference-demo"
    negative_path, eligible_path, review_path = create_reference_demo(output)
    negative = json.loads(negative_path.read_text(encoding="utf-8"))
    eligible = json.loads(eligible_path.read_text(encoding="utf-8"))
    html = review_path.read_text(encoding="utf-8")

    assert negative["qtg_quality_result"]["status"] == "NO_APTO"
    assert eligible["qtg_quality_result"]["status"] == "APTO"
    assert negative["operational_path"] == eligible["operational_path"] == "FORBIDDEN"
    assert negative["operational_effect"] is eligible["operational_effect"] is False
    assert negative["decision_authority"] is eligible["decision_authority"] is False
    assert negative["terminal_fingerprint"] in html
    assert eligible["terminal_fingerprint"] in html


def test_demo_does_not_replace_existing_output(tmp_path):
    output = tmp_path / "reference-demo"
    output.mkdir()
    sentinel = output / "my-notes.txt"
    sentinel.write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError, match="Output already exists"):
        create_reference_demo(output)
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_demo_replay_verifies_artifacts_without_writing(tmp_path):
    output = tmp_path / "reference-demo"
    negative_path, eligible_path, review_path = create_reference_demo(output)
    before = {p.name: p.read_bytes() for p in (negative_path, eligible_path, review_path)}
    fingerprints = verify_reference_demo(output)
    assert fingerprints == tuple(json.loads(p.read_text(encoding="utf-8"))["terminal_fingerprint"]
                                 for p in (negative_path, eligible_path))
    assert before == {p.name: p.read_bytes() for p in (negative_path, eligible_path, review_path)}


def test_demo_replay_detects_html_drift(tmp_path):
    output = tmp_path / "reference-demo"
    _, _, review_path = create_reference_demo(output)
    review_path.write_text("stale review", encoding="utf-8")
    with pytest.raises(ValueError, match="Review HTML differs"):
        verify_reference_demo(output)


def test_demo_exports_and_replays_both_price_observations(tmp_path):
    output = tmp_path / "reference-with-price"
    files = create_reference_demo(output, with_price=True)
    assert len(files) == 5
    negative, eligible = (json.loads(files[i].read_text(encoding="utf-8"))
                          for i in (0, 1))
    negative_price, eligible_price = (json.loads(files[i].read_text(encoding="utf-8"))
                                      for i in (3, 4))
    html = files[2].read_text(encoding="utf-8")
    assert negative_price["terminal_fingerprint"] == negative["terminal_fingerprint"]
    assert eligible_price["terminal_fingerprint"] == eligible["terminal_fingerprint"]
    assert negative["qtg_quality_result"]["status"] == "NO_APTO"
    assert negative_price["price_result"]["pr_status"] == "PR_AVAILABLE"
    assert html.count("Observación PRICE sintética") == 2
    assert "no es un techo" in html
    assert "20.25 EUR" in html
    assert verify_reference_demo(output) == (
        negative["terminal_fingerprint"], eligible["terminal_fingerprint"],
    )


def test_demo_rejects_incomplete_or_changed_price_sidecar(tmp_path):
    output = tmp_path / "reference-with-price"
    files = create_reference_demo(output, with_price=True)
    files[4].unlink()
    with pytest.raises(ValueError, match="Both PRICE observations"):
        verify_reference_demo(output)
    files[4].write_bytes(files[3].read_bytes())
    with pytest.raises(ValueError, match="PRICE observation identity"):
        verify_reference_demo(output)


def test_demo_rejects_changed_price_value(tmp_path):
    output = tmp_path / "reference-with-price"
    files = create_reference_demo(output, with_price=True)
    altered = json.loads(files[3].read_text(encoding="utf-8"))
    altered["price_result"]["pr_value"] = "999.00"
    files[3].write_text(json.dumps(altered), encoding="utf-8")
    with pytest.raises(ValueError, match="PRICE observation fingerprint"):
        verify_reference_demo(output)


@pytest.mark.parametrize("with_price", [False, True])
def test_demo_exports_and_replays_tco_observations(tmp_path, with_price):
    output = tmp_path / "reference-with-tco"
    files = create_reference_demo(output, with_price=with_price, with_tco=True)
    assert len(files) == (7 if with_price else 5)
    negative = json.loads(files[0].read_text(encoding="utf-8"))
    eligible = json.loads(files[1].read_text(encoding="utf-8"))
    negative_tco, eligible_tco = (
        json.loads((output / name).read_text(encoding="utf-8"))
        for name in ("reference-negative-tco.json", "reference-tco.json")
    )
    html = files[2].read_text(encoding="utf-8")
    assert negative_tco["terminal_fingerprint"] == negative["terminal_fingerprint"]
    assert eligible_tco["terminal_fingerprint"] == eligible["terminal_fingerprint"]
    assert negative_tco["tco_result"]["value"] == "205.00"
    assert negative_tco["trace_references"] == []
    assert html.count("Observación TCO sintética") == 2
    assert html.count("Coste de adquisición modelado") == 2
    assert "lo no informado no equivale a coste cero" in html
    assert html.count("Observación PRICE sintética") == (2 if with_price else 0)
    assert verify_reference_demo(output) == (
        negative["terminal_fingerprint"], eligible["terminal_fingerprint"],
    )


def test_demo_rejects_missing_or_tampered_tco_sidecar(tmp_path):
    output = tmp_path / "reference-with-tco"
    create_reference_demo(output, with_tco=True)
    negative_tco = output / "reference-negative-tco.json"
    eligible_tco = output / "reference-tco.json"
    eligible_tco.unlink()
    with pytest.raises(ValueError, match="Both TCO observations"):
        verify_reference_demo(output)
    eligible_tco.write_bytes(negative_tco.read_bytes())
    with pytest.raises(ValueError, match="TCO observation identity"):
        verify_reference_demo(output)
    altered = json.loads(negative_tco.read_text(encoding="utf-8"))
    altered["tco_result"]["value"] = "999.00"
    negative_tco.write_text(json.dumps(altered), encoding="utf-8")
    with pytest.raises(ValueError, match="TCO observation fingerprint"):
        verify_reference_demo(output)


@pytest.mark.parametrize("with_price,with_tco", [(False, False), (True, True)])
def test_demo_exports_and_replays_declared_supplier_assessment(tmp_path, with_price, with_tco):
    output = tmp_path / "reference-with-supplier"
    files = create_reference_demo(
        output, with_price=with_price, with_tco=with_tco, with_supplier_risk=True,
    )
    assert len(files) == (9 if with_price else 5)
    negative = json.loads(files[0].read_text(encoding="utf-8"))
    supplier = json.loads((output / "reference-negative-supplier-risk.json").read_text(
        encoding="utf-8",
    ))
    html = files[2].read_text(encoding="utf-8")
    assert supplier["terminal_fingerprint"] == negative["terminal_fingerprint"]
    assert supplier["assessment_origin"] == "DECLARED_SYNTHETIC_EXTERNAL_ASSESSMENT"
    assert not any(supplier["source_inventory"].values())
    assert html.count("Observación Supplier Risk/Value sintética") == 2
    assert "RELIABILITY=FAVORABLE" in html
    assert "no se deduce de hechos de desempeño" in html
    assert html.count("Observación PRICE sintética") == (2 if with_price else 0)
    assert html.count("Observación TCO sintética") == (2 if with_tco else 0)
    assert verify_reference_demo(output)[0] == negative["terminal_fingerprint"]


def test_demo_rejects_missing_or_altered_supplier_sidecar(tmp_path):
    output = tmp_path / "reference-with-supplier"
    create_reference_demo(output, with_supplier_risk=True)
    negative = output / "reference-negative-supplier-risk.json"
    eligible = output / "reference-supplier-risk.json"
    eligible.unlink()
    with pytest.raises(ValueError, match="Both SUPPLIER_RISK_VALUE observations"):
        verify_reference_demo(output)
    eligible.write_bytes(negative.read_bytes())
    with pytest.raises(ValueError, match="Supplier observation identity"):
        verify_reference_demo(output)
    altered = json.loads(negative.read_text(encoding="utf-8"))
    altered["supplier_result"]["risk_dimensions"][0]["state"] = "ADVERSE"
    negative.write_text(json.dumps(altered), encoding="utf-8")
    with pytest.raises(ValueError, match="Supplier observation fingerprint"):
        verify_reference_demo(output)


@pytest.mark.parametrize("with_others", [False, True])
def test_demo_exports_and_replays_c0_with_qtg_context(tmp_path, with_others):
    output = tmp_path / "reference-with-c0"
    files = create_reference_demo(
        output, with_c0=True, with_price=with_others,
        with_tco=with_others, with_supplier_risk=with_others,
    )
    assert len(files) == (11 if with_others else 5)
    negative, eligible = (json.loads((output / name).read_text(encoding="utf-8"))
                          for name in ("reference-negative-c0.json", "reference-c0.json"))
    assert (negative["qtg_status"], eligible["qtg_status"]) == ("NO_APTO", "APTO")
    assert negative["vertical_result"]["assessments"] == eligible["vertical_result"]["assessments"]
    assert negative["qtg_c0_derivation_proven"] is False
    assert negative["base_result"] == "COMPRAR"
    html = files[2].read_text(encoding="utf-8")
    assert html.count("Observación C0/CRC sintética") == 2
    assert "Un C0 COMPLETED no equivale a QTG APTO" in html
    assert "no son una orden" in html
    assert verify_reference_demo(output) == tuple(
        json.loads(files[i].read_text(encoding="utf-8"))["terminal_fingerprint"]
        for i in (0, 1)
    )


def test_demo_rejects_missing_or_modified_c0_sidecar(tmp_path):
    output = tmp_path / "reference-with-c0"
    create_reference_demo(output, with_c0=True)
    negative = output / "reference-negative-c0.json"
    eligible = output / "reference-c0.json"
    eligible.unlink()
    with pytest.raises(ValueError, match="Both C0 observations"):
        verify_reference_demo(output)
    eligible.write_bytes(negative.read_bytes())
    with pytest.raises(ValueError, match="C0 observation identity"):
        verify_reference_demo(output)
    modified = json.loads(negative.read_text(encoding="utf-8"))
    modified["crc_result"]["consolidated_result"] = "NO COMPRAR"
    negative.write_text(json.dumps(modified), encoding="utf-8")
    with pytest.raises(ValueError, match="C0 observation fingerprint"):
        verify_reference_demo(output)


@pytest.mark.parametrize("combined", [False, True])
def test_demo_exports_and_replays_structural_decision_twin(tmp_path, combined):
    output = tmp_path / "reference-with-twin"
    files = create_reference_demo(
        output, with_decision_twin=True, with_price=combined,
        with_tco=combined, with_supplier_risk=combined, with_c0=combined,
    )
    assert len(files) == (13 if combined else 5)
    negative = json.loads(files[0].read_text(encoding="utf-8"))
    twin = json.loads((output / "reference-negative-decision-twin.json").read_text(
        encoding="utf-8",
    ))
    assert twin["terminal_fingerprint"] == negative["terminal_fingerprint"]
    assert twin["selected_alternative"] is None
    assert twin["differences"] == []
    assert len(twin["alternative_refs"]) == 2
    html = files[2].read_text(encoding="utf-8")
    assert html.count("Observación Decision Twin sintética") == 2
    assert "No hay puntuación, ranking, preferencia" in html
    assert "no demuestra equivalencia comercial universal" in html
    assert verify_reference_demo(output)[0] == negative["terminal_fingerprint"]


def test_demo_rejects_missing_or_tampered_twin_sidecar(tmp_path):
    output = tmp_path / "reference-with-twin"
    create_reference_demo(output, with_decision_twin=True)
    negative = output / "reference-negative-decision-twin.json"
    eligible = output / "reference-decision-twin.json"
    eligible.unlink()
    with pytest.raises(ValueError, match="Both DECISION_TWIN observations"):
        verify_reference_demo(output)
    eligible.write_bytes(negative.read_bytes())
    with pytest.raises(ValueError, match="Decision Twin observation identity"):
        verify_reference_demo(output)
    altered = json.loads(negative.read_text(encoding="utf-8"))
    altered["comparison"]["differences"] = ["viability"]
    negative.write_text(json.dumps(altered), encoding="utf-8")
    with pytest.raises(ValueError, match="Decision Twin observation fingerprint"):
        verify_reference_demo(output)


@pytest.mark.parametrize("combined", [False, True])
def test_demo_exports_and_replays_scenario_coordination(tmp_path, combined):
    output = tmp_path / "reference-with-scenarios"
    files = create_reference_demo(
        output, with_scenario_coordination=True, with_price=combined,
        with_tco=combined, with_supplier_risk=combined, with_c0=combined,
        with_decision_twin=combined,
    )
    assert len(files) == (15 if combined else 5)
    negative = json.loads(files[0].read_text(encoding="utf-8"))
    scenario = json.loads((output / "reference-negative-scenario-coordination.json").read_text(
        encoding="utf-8",
    ))
    assert scenario["terminal_fingerprint"] == negative["terminal_fingerprint"]
    assert scenario["selected_scenario"] is None
    assert len(scenario["scenario_ids"]) == 2
    assert [item["values"]["viability_result"]["status"]
            for item in scenario["support"]["scenarios"]] == ["VIABLE", "VIABLE"]
    html = files[2].read_text(encoding="utf-8")
    assert html.count("Observación Scenario Coordination sintética") == 2
    assert "no demuestra una diferencia de viabilidad de negocio" in html
    assert "no elige, prioriza ni autoriza" in html
    assert html.count("Observación Decision Twin sintética") == (2 if combined else 0)
    assert verify_reference_demo(output)[0] == negative["terminal_fingerprint"]


def test_demo_rejects_missing_or_tampered_scenario_sidecar(tmp_path):
    output = tmp_path / "reference-with-scenarios"
    create_reference_demo(output, with_scenario_coordination=True)
    negative = output / "reference-negative-scenario-coordination.json"
    eligible = output / "reference-scenario-coordination.json"
    eligible.unlink()
    with pytest.raises(ValueError, match="Both SCENARIO_COORDINATION observations"):
        verify_reference_demo(output)
    eligible.write_bytes(negative.read_bytes())
    with pytest.raises(ValueError, match="Scenario observation identity"):
        verify_reference_demo(output)
    changed = json.loads(negative.read_text(encoding="utf-8"))
    changed["support"]["scenarios"][0]["status"] = "BLOCKED"
    negative.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(ValueError, match="Scenario observation fingerprint"):
        verify_reference_demo(output)
