"""Provenance-safe, same-call reference O2 observation."""
from copy import deepcopy

import pytest

from examples.reference_business_case_001 import (
    _bundle, _runtime, _scenario_sources, execute_reference_business_case,
    execute_reference_business_case_with_scenario_coordination_observation,
)
from eios.core.reference_scenario_coordination_observation import (
    validate_reference_scenario_coordination_observation_payload,
)
from eios.rules.scenario_integration import (
    build_reference_observed_scenario_coordination_invoker,
)


@pytest.mark.parametrize("variant", ("negative", "qtg-eligible"))
def test_same_run_support_and_terminal_unchanged(variant):
    baseline = execute_reference_business_case(variant=variant).to_payload()
    terminal, observation = execute_reference_business_case_with_scenario_coordination_observation(
        variant=variant,
    )
    payload = observation.to_payload()
    assert terminal.to_payload() == baseline
    validate_reference_scenario_coordination_observation_payload(payload, baseline)
    assert len(payload["scenario_ids"]) == 2
    assert [item["status"] for item in payload["support"]["scenarios"]] == ["COMPLETED"] * 2
    assert payload["selected_scenario"] is None
    assert payload["scenario_execution"] == next(
        item for item in baseline["execution_outcome"]["capability_results"]
        if item["capability"] == "SCENARIO_COORDINATION"
    )
    changed = deepcopy(payload)
    changed["support"]["scenarios"][0]["status"] = "BLOCKED"
    with pytest.raises(ValueError, match="fingerprint"):
        validate_reference_scenario_coordination_observation_payload(changed, baseline)


def test_rehashed_detached_support_is_rejected():
    from eios.core.reference_price_observation import _canonical
    from hashlib import sha256

    terminal, observation = execute_reference_business_case_with_scenario_coordination_observation(
        variant="negative",
    )
    payload = observation.to_payload()
    payload["support"]["scenarios"][0]["values"]["extra"] = "invented"
    payload["support_fingerprint"] = sha256(_canonical(payload["support"])).hexdigest()
    payload["observation_fingerprint"] = sha256(_canonical({
        key: value for key, value in payload.items() if key != "observation_fingerprint"
    })).hexdigest()
    with pytest.raises(ValueError, match="provenanced replay"):
        validate_reference_scenario_coordination_observation_payload(
            payload, terminal.to_payload(),
        )


def test_foreign_root_and_single_use():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    preparation, inputs, _ = _scenario_sources(purchase, context)
    observed = build_reference_observed_scenario_coordination_invoker(
        purchase=purchase, preparation=preparation,
        inputs=inputs, reference_case_id="test-case",
    )
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()
    with pytest.raises(ValueError, match="currency"):
        observed(purchase.model_copy(update={"currency": "USD"}), context)
    with pytest.raises(ValueError, match="single-use"):
        observed(purchase, context)

    valid = build_reference_observed_scenario_coordination_invoker(
        purchase=purchase, preparation=preparation,
        inputs=inputs, reference_case_id="test-case",
    )
    with pytest.raises(ValueError, match="scenario_id"):
        valid(purchase, context.model_copy(update={"scenario_id": "other"}))
    valid = build_reference_observed_scenario_coordination_invoker(
        purchase=purchase, preparation=preparation,
        inputs=inputs, reference_case_id="test-case",
    )
    capability = valid(purchase, context)
    assert valid.capture().capability == capability
    with pytest.raises(ValueError, match="single-use"):
        valid(purchase, context)
