"""TCO capture must preserve the actual same-run synthetic computation."""
import copy

import pytest

from examples.reference_business_case_001 import (
    _bundle, _runtime, execute_reference_business_case,
    execute_reference_business_case_with_tco_observation,
)
from eios.core.reference_tco_observation import (
    validate_reference_tco_observation_payload,
)
from eios.core.tco_integration import build_reference_observed_tco_invoker
from eios.tco.models import CostComponent, TCOInput


@pytest.mark.parametrize("variant", ["negative", "qtg-eligible"])
def test_same_run_capture_preserves_terminal_and_scope(variant):
    baseline = execute_reference_business_case(variant=variant).to_payload()
    terminal, observation = execute_reference_business_case_with_tco_observation(
        variant=variant,
    )
    payload = observation.to_payload()
    assert terminal.to_payload() == baseline
    validate_reference_tco_observation_payload(payload, baseline)
    assert payload["tco_result"]["value"] == "205.00"
    assert payload["contributing_components"] == ["ACQUISITION"]
    assert payload["trace_references"] == []
    assert payload["additional_attributable_costs_provided"] is False
    assert payload["tco_execution"] == next(
        item for item in baseline["execution_outcome"]["capability_results"]
        if item["capability"] == "TCO"
    )
    changed = copy.deepcopy(payload)
    changed["tco_result"]["value"] = "0"
    with pytest.raises(ValueError):
        validate_reference_tco_observation_payload(changed, baseline)


def test_one_production_and_rejection_before_production(monkeypatch):
    purchase, context = _runtime(_bundle()[1])
    payload = TCOInput(purchase_operation=purchase)
    import eios.core.tco_integration as integration
    original = integration.calculate_tco
    calls = []
    monkeypatch.setattr(integration, "calculate_tco",
                        lambda source: (calls.append(source), original(source))[1])
    observed = build_reference_observed_tco_invoker(
        payload=payload, reference_case_id="test-case",
    )
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()
    with pytest.raises(ValueError, match="no coincide"):
        observed(purchase.model_copy(update={"quantity": purchase.quantity + 1}), context)
    assert calls == []
    with pytest.raises(ValueError, match="single-use"):
        observed(purchase, context)

    valid = build_reference_observed_tco_invoker(
        payload=payload, reference_case_id="test-case",
    )
    execution = valid(purchase, context)
    assert len(calls) == 1
    assert valid.capture().capability == execution
    with pytest.raises(ValueError, match="single-use"):
        valid(purchase, context)
    assert len(calls) == 1
    assert valid.capture().result.value == 205


def test_incomplete_result_is_retained_without_invented_traces():
    purchase, context = _runtime(_bundle()[1])
    observed = build_reference_observed_tco_invoker(
        payload=TCOInput(
            purchase_operation=purchase,
            attributable_costs=(CostComponent(
                component="TRANSPORT", amount=None, currency="EUR",
                attribution_ref="synthetic:transport", rule_reference="TEST-TCO",
            ),),
        ),
        reference_case_id="test-case",
    )
    capability = observed(purchase, context)
    capture = observed.capture()
    assert capture.result.value is None
    assert "TRANSPORT" in capture.result.unresolved_components
    assert capability.status == "PARTIALLY_COMPLETED"
    assert capability.result_available is False
    assert capability.trace_references == ()
