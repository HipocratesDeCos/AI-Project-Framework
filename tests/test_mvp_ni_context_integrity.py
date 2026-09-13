from decimal import Decimal
from inspect import signature

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
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


def test_ni_invoker_receives_current_purchase_and_context_without_mutation():
    purchase = _purchase()
    context = _context()
    purchase_before = purchase.model_dump(mode="python")
    context_before = context.model_dump(mode="python")
    seen: list[tuple[dict, dict]] = []

    def ni_invoker(received_purchase, received_context):
        seen.append(
            (
                received_purchase.model_dump(mode="python"),
                received_context.model_dump(mode="python"),
            )
        )
        return CapabilityExecution(
            capability="NEGOTIATION_INTELLIGENCE",
            status=O1ExecutionStatus.COMPLETED,
            result_available=True,
            trace_references=("TRACE-NI-1",),
        )

    outcome = run_mvp_execution(
        purchase=purchase,
        context=context,
        policy_version="MVP-NI-QUARANTINE-1",
        negotiation_intelligence_invoker=ni_invoker,
    )

    assert tuple(item.capability for item in outcome.capability_results) == (
        "NEGOTIATION_INTELLIGENCE",
    )
    assert seen == [(purchase_before, context_before)]
    assert purchase.model_dump(mode="python") == purchase_before
    assert context.model_dump(mode="python") == context_before


def test_ni_raw_result_is_not_a_public_composition_parameter():
    parameters = signature(run_mvp_execution).parameters

    assert "negotiation_intelligence_result" not in parameters
    assert "negotiation_intelligence_invoker" in parameters
