"""Joint review rejects incompatible, individually valid synthetic captures."""
from copy import deepcopy
from hashlib import sha256

import pytest

from examples.reference_business_case_001 import execute_reference_business_case_with_selected_observations
from examples.reference_business_case_review import render_review
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.reference_ni_observation import validate_reference_ni_observation_payload
from eios.core.reference_price_observation import _canonical
from eios.rules.negotiation_provenance import NegotiationContentEvidence, _produce_c0_bound_ni
from eios.rules.provenance import AssessmentTraceBinding


def _pair():
    runs = [execute_reference_business_case_with_selected_observations(
        variant=variant, with_c0=True, with_decision_twin=True,
        with_scenario_coordination=True, with_negotiation_intelligence=True,
        with_negotiation_ladder=True,
    ) for variant in ("negative", "qtg-eligible")]
    terminals = tuple(run.to_payload() for run, _ in runs)
    captures = {key: tuple(items[key].to_payload() for _, items in runs)
                for key in runs[0][1]}
    return terminals, captures


def _render(terminals, captures):
    return render_review(*terminals, c0_observations=captures["c0"],
                         twin_observations=captures["decision_twin"],
                         scenario_observations=captures["scenario_coordination"],
                         ni_observations=captures["negotiation_intelligence"],
                         ladder_observations=captures["negotiation_ladder"])


def _digest(value):
    return sha256(_canonical(value)).hexdigest()


def test_joint_review_accepts_same_run_sources_for_both_variants():
    terminals, captures = _pair()
    html = _render(terminals, captures)
    assert html.count("Observación Negotiation Ladder sintética") == 2
    assert html.count("Observación Scenario Coordination sintética") == 2


def test_joint_review_rejects_individually_valid_alternative_ni_source():
    terminals, captures = _pair()
    ni = deepcopy(captures["negotiation_intelligence"][0])
    source = ni["source"]
    source["content_evidence"]["negotiation_content"]["objective"] = \
        "Different fictional negotiation objective"
    purchase = PurchaseOperation.model_validate(source["purchase"])
    context = DecisionContext.model_validate(terminals[0]["context"])
    result = _produce_c0_bound_ni(
        purchase=purchase, context=context,
        content_evidence=NegotiationContentEvidence.model_validate(source["content_evidence"]),
        evidences=tuple(Evidence.model_validate(item) for item in source["evidences"]),
        bindings=tuple(AssessmentTraceBinding.model_validate(item) for item in source["bindings"]),
    )
    ni["ni_result"] = result.model_dump(mode="json")
    ni["source_fingerprint"] = _digest(source)
    ni["ni_result_fingerprint"] = _digest(ni["ni_result"])
    ni["observation_fingerprint"] = _digest({
        key: value for key, value in ni.items() if key != "observation_fingerprint"
    })
    validate_reference_ni_observation_payload(ni, terminals[0])
    captures["negotiation_intelligence"] = (ni, captures["negotiation_intelligence"][1])
    with pytest.raises(ValueError, match="NI and Ladder observations have different sources"):
        _render(terminals, captures)
