from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.negotiation_intelligence import (
    NIContextReferences,
    NegotiationContent,
    NegotiationIntelligenceResult,
)
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-NI-CTX",
        scenario_id="S-NI-CTX",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-NI-CTX",
        scenario_id="S-NI-CTX",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-12",
    )


def _ni_result(**reference_overrides) -> NegotiationIntelligenceResult:
    references = {
        "decision_id": "D-NI-CTX",
        "scenario_id": "S-NI-CTX",
        "rules_version": "rules-v1",
        "parameters_version": "params-v1",
        "data_snapshot_id": "snapshot-v1",
        "viability_reference": "VF-1",
        "decision_twin_reference": "DT-1",
        "evidence_references": ("E-1",),
    }
    references.update(reference_overrides)
    return NegotiationIntelligenceResult(
        negotiation_result_id="NI-CTX-1",
        context_references=NIContextReferences(**references),
        negotiation_content=NegotiationContent(
            objective="Preserve authorized negotiation content"
        ),
        traceability_references=("TRACE-NI-1",),
    )


def test_matching_ni_context_executes_without_mutation():
    context = _context()
    result = _ni_result()
    context_before = context.model_dump()
    result_before = result.model_dump()

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=context,
        policy_version="MVP-NI-CTX-1",
        negotiation_intelligence_result=result,
    )

    assert tuple(item.capability for item in outcome.capability_results) == (
        "NEGOTIATION_INTELLIGENCE",
    )
    assert outcome.capability_results[0].result_available is True
    assert context.model_dump() == context_before
    assert result.model_dump() == result_before


def test_optional_ni_context_references_may_be_absent():
    result = _ni_result(
        scenario_id=None,
        rules_version=None,
        parameters_version=None,
        data_snapshot_id=None,
    )

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-NI-CTX-1",
        negotiation_intelligence_result=result,
    )

    assert outcome.capability_results[0].capability == "NEGOTIATION_INTELLIGENCE"
    assert outcome.capability_results[0].result_available is True


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "D-OTHER"),
        ("scenario_id", "S-OTHER"),
        ("rules_version", "rules-other"),
        ("parameters_version", "params-other"),
        ("data_snapshot_id", "snapshot-other"),
    ),
)
def test_ni_context_mismatch_is_rejected(field: str, value: str):
    result = _ni_result(**{field: value})

    with pytest.raises(ValueError, match=field):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-NI-CTX-1",
            negotiation_intelligence_result=result,
        )


def test_ni_context_mismatch_reports_all_incompatible_references():
    result = _ni_result(
        decision_id="D-OTHER",
        scenario_id="S-OTHER",
        rules_version="rules-other",
        parameters_version="params-other",
        data_snapshot_id="snapshot-other",
    )

    with pytest.raises(ValueError) as exc_info:
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-NI-CTX-1",
            negotiation_intelligence_result=result,
        )

    message = str(exc_info.value)
    for field in (
        "decision_id",
        "scenario_id",
        "rules_version",
        "parameters_version",
        "data_snapshot_id",
    ):
        assert field in message


def test_ni_context_mismatch_fails_before_any_capability_runs():
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
            policy_version="MVP-NI-CTX-1",
            rules_invoker=c0_invoker,
            negotiation_intelligence_result=_ni_result(decision_id="D-OTHER"),
        )

    assert calls == []
