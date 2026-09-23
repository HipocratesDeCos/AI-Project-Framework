from datetime import date
from decimal import Decimal
from inspect import signature

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.negotiation_intelligence import NIAssertion, NegotiationContent
from eios.core.orchestration import O1ExecutionStatus
from eios.rules import (
    NegotiationContentEvidence,
    build_provenanced_negotiation_intelligence_invoker,
    build_provenanced_ni_ladder_invokers,
    produce_negotiation_intelligence,
    produce_negotiation_ladder,
)


def _context():
    return DecisionContext(
        decision_id="D-NI",
        scenario_id="S-NI",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="D-NI",
        scenario_id="S-NI",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 23),
    )


def _evidence():
    return (
        Evidence(
            evidence_id="E-AUTH",
            source_type="negotiation",
            source_ref="authority:negotiation",
            captured_at=date(2026, 9, 23),
            state="DEMONSTRATED",
            demonstration_ref="authority:negotiation:v1",
        ),
        Evidence(
            evidence_id="E-PRICE",
            source_type="price",
            source_ref="price:ref",
            captured_at=date(2026, 9, 23),
            state="DEMONSTRATED",
            demonstration_ref="price:ref:v1",
        ),
    )


def _carrier(**overrides):
    values = dict(
        decision_id="D-NI",
        scenario_id="S-NI",
        authority_ref="authority:negotiation:v1",
        decision_twin_reference="twin:comparison:1",
        viability_reference="vf:S-NI",
        negotiation_content=NegotiationContent(
            objective="reduce total cost",
            opening_request="request improved price",
            moves=("request 5% reduction", "request payment extension"),
            concessions=("offer volume commitment",),
            counterpart_requirements=("supplier confirms lead time",),
            tradeoffs=("price for volume",),
            packages=("price+term package",),
            alternatives=("retain current offer",),
            fallback="retain current offer",
            conditions=("do not exceed approved limit",),
            convenience_analysis=("commercial benefit remains conditional",),
        ),
        justification=(
            NIAssertion(
                content="Authorized price reference exists.",
                epistemic_type="FACT",
                confidence=1.0,
                source_references=("price:ref:v1",),
            ),
        ),
        evidence_refs=("E-PRICE",),
        trace_refs=("TRACE-A", "TRACE-B"),
        authority_state="AUTHORIZED",
    )
    values.update(overrides)
    return NegotiationContentEvidence(**values)


def test_authorized_carrier_produces_literal_ni_content():
    carrier = _carrier()
    result = produce_negotiation_intelligence(
        purchase=_purchase(),
        context=_context(),
        content_evidence=carrier,
        evidences=_evidence(),
    )
    assert result.negotiation_content == carrier.negotiation_content
    assert result.justification == carrier.justification
    assert result.context_references.decision_twin_reference == "twin:comparison:1"
    assert result.context_references.viability_reference == "vf:S-NI"
    assert result.context_references.evidence_references == ("E-PRICE",)


@pytest.mark.parametrize("state", ["NOT_AUTHORIZED", "NOT_DETERMINABLE", "CONFLICTING"])
def test_non_authorized_state_fails_closed(state):
    with pytest.raises(ValueError, match="no autorizado"):
        produce_negotiation_intelligence(
            purchase=_purchase(),
            context=_context(),
            content_evidence=_carrier(authority_state=state),
            evidences=_evidence(),
        )


def test_gap_authority_ref_fails_closed():
    evidences = (
        Evidence(
            evidence_id="E-AUTH",
            source_type="negotiation",
            source_ref="authority:negotiation",
            captured_at=date(2026, 9, 23),
            state="GAP",
        ),
        _evidence()[1],
    )
    with pytest.raises(ValueError, match="authority_ref no demostrada"):
        produce_negotiation_intelligence(
            purchase=_purchase(),
            context=_context(),
            content_evidence=_carrier(),
            evidences=evidences,
        )


def test_identity_mismatch_fails_closed():
    bad = _carrier(decision_id="OTHER")
    with pytest.raises(ValueError, match="decision_id incompatible"):
        produce_negotiation_intelligence(
            purchase=_purchase(),
            context=_context(),
            content_evidence=bad,
            evidences=_evidence(),
        )


def test_negotiation_result_id_is_deterministic():
    args = dict(
        purchase=_purchase(),
        context=_context(),
        content_evidence=_carrier(),
        evidences=_evidence(),
    )
    first = produce_negotiation_intelligence(**args)
    second = produce_negotiation_intelligence(**args)
    assert first.negotiation_result_id == second.negotiation_result_id
    assert first.negotiation_result_id.startswith("ni:D-NI:S-NI:")


def test_ladder_orders_only_authorized_representable_fields():
    ni = produce_negotiation_intelligence(
        purchase=_purchase(),
        context=_context(),
        content_evidence=_carrier(),
        evidences=_evidence(),
    )
    ladder = produce_negotiation_ladder(
        negotiation_result=ni,
        purchase=_purchase(),
        context=_context(),
    )

    assert [step.step_type for step in ladder.steps] == [
        "OBJECTIVE",
        "OPENING_REQUEST",
        "MOVE",
        "MOVE",
        "CONCESSION",
        "COUNTERPART_CONSIDERATION",
        "CONDITION",
        "ALTERNATIVE",
        "FALLBACK",
    ]
    refs = [step.source_content_reference for step in ladder.steps]
    assert not any("tradeoffs" in ref for ref in refs)
    assert not any("packages" in ref for ref in refs)
    assert not any("convenience_analysis" in ref for ref in refs)
    assert ladder.context_references.negotiation_result_id == ni.negotiation_result_id


def test_ladder_preserves_internal_collection_order_and_builds_linear_structure():
    ni = produce_negotiation_intelligence(
        purchase=_purchase(),
        context=_context(),
        content_evidence=_carrier(),
        evidences=_evidence(),
    )
    ladder = produce_negotiation_ladder(
        negotiation_result=ni,
        purchase=_purchase(),
        context=_context(),
    )
    move_refs = [
        step.source_content_reference
        for step in ladder.steps
        if step.step_type == "MOVE"
    ]
    assert move_refs[0].endswith(":moves:0")
    assert move_refs[1].endswith(":moves:1")
    assert len(ladder.transitions) == len(ladder.steps) - 1
    assert all(item.trigger_reference is None for item in ladder.transitions)
    assert len(ladder.routes) == 1
    assert ladder.routes[0].step_references == tuple(step.step_id for step in ladder.steps)


def test_ladder_id_is_deterministic():
    ni = produce_negotiation_intelligence(
        purchase=_purchase(),
        context=_context(),
        content_evidence=_carrier(),
        evidences=_evidence(),
    )
    first = produce_negotiation_ladder(
        negotiation_result=ni,
        purchase=_purchase(),
        context=_context(),
    )
    second = produce_negotiation_ladder(
        negotiation_result=ni,
        purchase=_purchase(),
        context=_context(),
    )
    assert first.ladder_id == second.ladder_id


def test_unrepresentable_only_content_rejects_ladder():
    carrier = _carrier(
        negotiation_content=NegotiationContent(
            tradeoffs=("price for volume",),
            packages=("bundle",),
            convenience_analysis=("analysis",),
        )
    )
    ni = produce_negotiation_intelligence(
        purchase=_purchase(),
        context=_context(),
        content_evidence=carrier,
        evidences=_evidence(),
    )
    with pytest.raises(ValueError, match="no representable"):
        produce_negotiation_ladder(
            negotiation_result=ni,
            purchase=_purchase(),
            context=_context(),
        )


def test_ni_invoker_is_o1_compatible():
    invoker = build_provenanced_negotiation_intelligence_invoker(
        content_evidence=_carrier(),
        evidences=_evidence(),
    )
    result = invoker(_purchase(), _context())
    assert result.capability == "NEGOTIATION_INTELLIGENCE"
    assert result.status == O1ExecutionStatus.COMPLETED
    assert result.result_available is True


def test_combined_invokers_are_o1_compatible_and_keep_canonical_order():
    ni_invoker, ladder_invoker = build_provenanced_ni_ladder_invokers(
        content_evidence=_carrier(),
        evidences=_evidence(),
    )
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="NI-LADDER-PROV-1",
        negotiation_intelligence_invoker=ni_invoker,
        negotiation_ladder_invoker=ladder_invoker,
    )
    assert tuple(item.capability for item in outcome.capability_results) == (
        "NEGOTIATION_INTELLIGENCE",
        "NEGOTIATION_LADDER",
    )
    assert all(item.status == O1ExecutionStatus.COMPLETED for item in outcome.capability_results)


def test_raw_results_remain_out_of_public_execution_signature():
    params = signature(run_mvp_execution).parameters
    assert "negotiation_intelligence_result" not in params
    assert "negotiation_ladder_result" not in params
    assert "negotiation_intelligence_invoker" in params
    assert "negotiation_ladder_invoker" in params


def test_carrier_is_frozen_and_duplicate_refs_are_rejected():
    carrier = _carrier()
    with pytest.raises(ValidationError):
        carrier.authority_state = "CONFLICTING"
    with pytest.raises(ValidationError, match="duplicados"):
        _carrier(evidence_refs=("E-PRICE", "E-PRICE"))
