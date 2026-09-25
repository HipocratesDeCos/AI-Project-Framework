"""Same-call supplier capture preserves synthetic declaration and provenance."""
from copy import deepcopy

import pytest

from examples.reference_business_case_001 import (
    _bundle, _provenanced_supplier_risk_invoker, _runtime,
    execute_reference_business_case,
    execute_reference_business_case_with_supplier_risk_observation,
)
from eios.core.reference_supplier_risk_observation import (
    validate_reference_supplier_risk_observation_payload,
)


@pytest.mark.parametrize("variant", ("negative", "qtg-eligible"))
def test_supplier_observation_is_same_run_synthetic_declaration(variant):
    baseline = execute_reference_business_case(variant=variant).to_payload()
    terminal, observation = execute_reference_business_case_with_supplier_risk_observation(
        variant=variant,
    )
    payload = observation.to_payload()
    assert terminal.to_payload() == baseline
    validate_reference_supplier_risk_observation_payload(payload, baseline)
    assert payload["assessment_origin"] == "DECLARED_SYNTHETIC_EXTERNAL_ASSESSMENT"
    assert payload["supplier_result"]["risk_dimensions"][0]["state"] == "FAVORABLE"
    assert payload["supplier_result"]["value_dimensions"] == []
    assert not any(payload["source_inventory"].values())
    assert payload["value_comparison_available"] is False
    assert payload["supplier_execution"] == next(
        item for item in baseline["execution_outcome"]["capability_results"]
        if item["capability"] == "SUPPLIER_RISK_VALUE"
    )
    altered = deepcopy(payload)
    altered["supplier_result"]["risk_dimensions"][0]["state"] = "ADVERSE"
    with pytest.raises(ValueError, match="fingerprint"):
        validate_reference_supplier_risk_observation_payload(altered, baseline)


def test_purchase_mismatch_rejected_before_production_and_session_consumed(monkeypatch):
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    import eios.supplier.risk_value as supplier_module
    original = supplier_module.produce_supplier_risk_value
    calls = []
    monkeypatch.setattr(supplier_module, "produce_supplier_risk_value",
                        lambda **kwargs: (calls.append(kwargs), original(**kwargs))[1])
    observed = _provenanced_supplier_risk_invoker(
        purchase, context, observed=True, reference_case_id="test-case",
    )
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()
    changed = purchase.model_copy(update={"unit_price": purchase.unit_price + 1})
    with pytest.raises(ValueError, match="unit_price"):
        observed(changed, context)
    assert calls == []
    with pytest.raises(ValueError, match="single-use"):
        observed(purchase, context)
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()

    valid = _provenanced_supplier_risk_invoker(
        purchase, context, observed=True, reference_case_id="test-case",
    )
    capability = valid(purchase, context)
    assert len(calls) == 1
    assert valid.capture().capability == capability
    with pytest.raises(ValueError, match="single-use"):
        valid(purchase, context)
    assert len(calls) == 1


def test_scenario_mismatch_rejected_before_production(monkeypatch):
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    observed = _provenanced_supplier_risk_invoker(
        purchase, context, observed=True, reference_case_id="test-case",
    )
    import eios.supplier.risk_value as supplier_module
    monkeypatch.setattr(supplier_module, "produce_supplier_risk_value",
                        lambda **kwargs: pytest.fail("producer called"))
    with pytest.raises(ValueError, match="scenario_id"):
        observed(purchase, context.model_copy(update={"scenario_id": "other"}))


def test_unresolved_external_assessment_is_preserved():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    template = _provenanced_supplier_risk_invoker(
        purchase, context, observed=True, reference_case_id="test-case",
    )
    supplier, risks, values, evidences = template._sources
    from eios.supplier.risk_value import build_reference_observed_supplier_risk_value_invoker
    observed = build_reference_observed_supplier_risk_value_invoker(
        reference_case_id="test-case", purchase=purchase,
        supplier_result=supplier,
        risk_assessments=(risks[0].model_copy(update={"state": "NOT_DETERMINABLE"}),),
        value_assessments=values, evidences=evidences,
    )
    capability = observed(purchase, context)
    capture = observed.capture()
    assert capability.status == "PARTIALLY_COMPLETED"
    assert capability.result_available is True
    assert capture.result.unresolved_items == (
        f"RISK:{purchase.supplier_id}:RELIABILITY:NOT_DETERMINABLE",
    )
    assert capability.trace_references == capture.result.trace_refs
