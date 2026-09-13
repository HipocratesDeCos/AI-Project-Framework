from decimal import Decimal
from inspect import signature

import pytest

from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-MVP",
        scenario_id="S-MVP",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-MVP",
        scenario_id="S-MVP",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-11",
    )


def _completed(capability: str, trace_reference: str) -> CapabilityExecution:
    return CapabilityExecution(
        capability=capability,
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=(trace_reference,),
    )


def _completed_c0(*_):
    return _completed("C0", "trace-c0")


def test_mvp_execution_runs_available_capabilities_in_canonical_order_and_context():
    purchase = _purchase()
    context = _context()
    seen: dict[str, tuple[dict, dict]] = {}

    def recording_invoker(capability: str, trace_reference: str):
        def invoke(received_purchase, received_context):
            seen[capability] = (
                received_purchase.model_dump(mode="python"),
                received_context.model_dump(mode="python"),
            )
            return _completed(capability, trace_reference)

        return invoke

    outcome = run_mvp_execution(
        purchase=purchase,
        context=context,
        policy_version="MVP-E2E-1",
        quality_invoker=recording_invoker("QTG", "trace-qtg"),
        tco_invoker=recording_invoker("TCO", "trace-tco"),
        rules_invoker=_completed_c0,
        decision_twin_invoker=recording_invoker("DECISION_TWIN", "trace-twin"),
        negotiation_intelligence_invoker=recording_invoker(
            "NEGOTIATION_INTELLIGENCE", "trace-ni"
        ),
        negotiation_ladder_invoker=recording_invoker(
            "NEGOTIATION_LADDER", "trace-ladder"
        ),
    )

    assert outcome.status == BoundaryStatus.COMPLETED
    assert tuple(item.capability for item in outcome.capability_results) == (
        "QTG",
        "TCO",
        "C0",
        "DECISION_TWIN",
        "NEGOTIATION_INTELLIGENCE",
        "NEGOTIATION_LADDER",
    )
    assert all(item.result_available for item in outcome.capability_results)
    expected = (
        purchase.model_dump(mode="python"),
        context.model_dump(mode="python"),
    )
    assert seen == {
        "QTG": expected,
        "TCO": expected,
        "DECISION_TWIN": expected,
        "NEGOTIATION_INTELLIGENCE": expected,
        "NEGOTIATION_LADDER": expected,
    }


def test_mvp_execution_preserves_partial_tco_state():
    def tco_invoker(*_):
        return CapabilityExecution(
            capability="TCO",
            status=O1ExecutionStatus.PARTIALLY_COMPLETED,
            result_available=False,
            unresolved_items=("TRANSPORT",),
        )

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-1",
        tco_invoker=tco_invoker,
    )

    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("TRANSPORT",)
    assert outcome.capability_results[0].capability == "TCO"
    assert outcome.capability_results[0].result_available is False


def test_mvp_execution_accepts_other_capabilities_without_opaque_invokers():
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-1",
        rules_invoker=_completed_c0,
    )

    assert tuple(item.capability for item in outcome.capability_results) == ("C0",)


def test_mvp_execution_public_signature_has_no_detached_opaque_results():
    parameters = signature(run_mvp_execution).parameters

    for raw_result in (
        "quality_result",
        "price_result",
        "tco_result",
        "decision_twin_result",
        "negotiation_intelligence_result",
        "negotiation_ladder_result",
    ):
        assert raw_result not in parameters

    for invoker in (
        "quality_invoker",
        "price_invoker",
        "tco_invoker",
        "decision_twin_invoker",
        "negotiation_intelligence_invoker",
        "negotiation_ladder_invoker",
    ):
        assert invoker in parameters


def test_mvp_execution_requires_at_least_one_capability():
    with pytest.raises(ValueError, match="al menos una capacidad"):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-E2E-1",
        )


def test_mvp_execution_rejects_context_mismatch_through_boundary():
    purchase = _purchase().model_copy(update={"scenario_id": "OTHER"})
    with pytest.raises(ValueError, match="scenario_id"):
        run_mvp_execution(
            purchase=purchase,
            context=_context(),
            policy_version="MVP-E2E-1",
            rules_invoker=_completed_c0,
        )
