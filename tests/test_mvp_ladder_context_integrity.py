from decimal import Decimal
from inspect import signature

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
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


def _completed(capability: str, trace: str) -> CapabilityExecution:
    return CapabilityExecution(
        capability=capability,
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=(trace,),
    )


def test_ladder_invoker_receives_current_purchase_and_context_without_mutation():
    purchase = _purchase()
    context = _context()
    purchase_before = purchase.model_dump(mode="python")
    context_before = context.model_dump(mode="python")
    seen: list[tuple[dict, dict]] = []

    def ladder_invoker(received_purchase, received_context):
        seen.append(
            (
                received_purchase.model_dump(mode="python"),
                received_context.model_dump(mode="python"),
            )
        )
        return _completed("NEGOTIATION_LADDER", "TRACE-LADDER-1")

    outcome = run_mvp_execution(
        purchase=purchase,
        context=context,
        policy_version="MVP-LADDER-QUARANTINE-1",
        negotiation_ladder_invoker=ladder_invoker,
    )

    assert tuple(item.capability for item in outcome.capability_results) == (
        "NEGOTIATION_LADDER",
    )
    assert seen == [(purchase_before, context_before)]
    assert purchase.model_dump(mode="python") == purchase_before
    assert context.model_dump(mode="python") == context_before


def test_ni_and_ladder_invokers_preserve_canonical_relative_order():
    calls: list[str] = []

    def ni_invoker(*_):
        calls.append("NEGOTIATION_INTELLIGENCE")
        return _completed("NEGOTIATION_INTELLIGENCE", "TRACE-NI-1")

    def ladder_invoker(*_):
        calls.append("NEGOTIATION_LADDER")
        return _completed("NEGOTIATION_LADDER", "TRACE-LADDER-1")

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-LADDER-QUARANTINE-1",
        negotiation_intelligence_invoker=ni_invoker,
        negotiation_ladder_invoker=ladder_invoker,
    )

    assert calls == ["NEGOTIATION_INTELLIGENCE", "NEGOTIATION_LADDER"]
    assert tuple(item.capability for item in outcome.capability_results) == (
        "NEGOTIATION_INTELLIGENCE",
        "NEGOTIATION_LADDER",
    )


def test_ladder_raw_result_is_not_a_public_composition_parameter():
    parameters = signature(run_mvp_execution).parameters

    assert "negotiation_ladder_result" not in parameters
    assert "negotiation_ladder_invoker" in parameters
