from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.negotiation_intelligence import (
    NIContextReferences,
    NegotiationContent,
    NegotiationIntelligenceResult,
)
from eios.core.negotiation_ladder import (
    LadderContextReferences,
    LadderStep,
    NegotiationLadderResult,
)
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-LADDER-CTX",
        scenario_id="S-LADDER-CTX",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-LADDER-CTX",
        scenario_id="S-LADDER-CTX",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-12",
    )


def _ni_result(result_id: str = "NI-LADDER-1") -> NegotiationIntelligenceResult:
    return NegotiationIntelligenceResult(
        negotiation_result_id=result_id,
        context_references=NIContextReferences(
            decision_id="D-LADDER-CTX",
            scenario_id="S-LADDER-CTX",
            rules_version="rules-v1",
            parameters_version="params-v1",
            data_snapshot_id="snapshot-v1",
        ),
        negotiation_content=NegotiationContent(
            objective="Preserve authorized negotiation content"
        ),
        traceability_references=("TRACE-NI-1",),
    )


def _ladder_result(**reference_overrides) -> NegotiationLadderResult:
    references = {
        "negotiation_result_id": "NI-LADDER-1",
        "decision_id": "D-LADDER-CTX",
        "scenario_id": "S-LADDER-CTX",
        "source_references": ("NI-CONTENT-1",),
    }
    references.update(reference_overrides)
    return NegotiationLadderResult(
        ladder_id="LADDER-CTX-1",
        context_references=LadderContextReferences(**references),
        steps=(
            LadderStep(
                step_id="STEP-1",
                step_type="OBJECTIVE",
                source_content_reference="NI-CONTENT-1",
                position=1,
            ),
        ),
        traceability_references=("TRACE-LADDER-1",),
    )


def test_matching_ladder_context_executes_without_mutation():
    context = _context()
    result = _ladder_result()
    context_before = context.model_dump()
    result_before = result.model_dump()

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=context,
        policy_version="MVP-LADDER-CTX-1",
        negotiation_ladder_result=result,
    )

    assert tuple(item.capability for item in outcome.capability_results) == (
        "NEGOTIATION_LADDER",
    )
    assert outcome.capability_results[0].result_available is True
    assert context.model_dump() == context_before
    assert result.model_dump() == result_before


def test_optional_ladder_scenario_reference_may_be_absent():
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-LADDER-CTX-1",
        negotiation_ladder_result=_ladder_result(scenario_id=None),
    )

    assert outcome.capability_results[0].capability == "NEGOTIATION_LADDER"


def test_ladder_without_ni_does_not_require_external_ni_materialization():
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-LADDER-CTX-1",
        negotiation_ladder_result=_ladder_result(
            negotiation_result_id="NI-EXTERNAL-NOT-PROVIDED"
        ),
    )

    assert outcome.capability_results[0].capability == "NEGOTIATION_LADDER"


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "D-OTHER"),
        ("scenario_id", "S-OTHER"),
    ),
)
def test_ladder_context_mismatch_is_rejected(field: str, value: str):
    with pytest.raises(ValueError, match=field):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-LADDER-CTX-1",
            negotiation_ladder_result=_ladder_result(**{field: value}),
        )


def test_ladder_and_ni_with_matching_upstream_identity_execute():
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-LADDER-CTX-1",
        negotiation_intelligence_result=_ni_result("NI-LADDER-1"),
        negotiation_ladder_result=_ladder_result(
            negotiation_result_id="NI-LADDER-1"
        ),
    )

    assert tuple(item.capability for item in outcome.capability_results) == (
        "NEGOTIATION_INTELLIGENCE",
        "NEGOTIATION_LADDER",
    )


def test_ladder_and_ni_with_different_upstream_identity_are_rejected():
    with pytest.raises(ValueError, match="negotiation_result_id"):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-LADDER-CTX-1",
            negotiation_intelligence_result=_ni_result("NI-AUTHORIZED"),
            negotiation_ladder_result=_ladder_result(
                negotiation_result_id="NI-OTHER"
            ),
        )


def test_ladder_reports_all_verifiable_mismatches():
    with pytest.raises(ValueError) as exc_info:
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-LADDER-CTX-1",
            negotiation_intelligence_result=_ni_result("NI-AUTHORIZED"),
            negotiation_ladder_result=_ladder_result(
                decision_id="D-OTHER",
                scenario_id="S-OTHER",
                negotiation_result_id="NI-OTHER",
            ),
        )

    message = str(exc_info.value)
    assert "decision_id" in message
    assert "scenario_id" in message
    assert "negotiation_result_id" in message


def test_ladder_context_mismatch_fails_before_any_capability_runs():
    calls: list[str] = []

    def c0_invoker(*_):
        calls.append("C0")
        return CapabilityExecution(
            capability="C0",
            status=O1ExecutionStatus.COMPLETED,
            result_available=True,
        )

    with pytest.raises(ValueError, match="decision_id"):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-LADDER-CTX-1",
            rules_invoker=c0_invoker,
            negotiation_ladder_result=_ladder_result(decision_id="D-OTHER"),
        )

    assert calls == []
