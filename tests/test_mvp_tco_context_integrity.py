from decimal import Decimal

import pytest

from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.tco.models import TCOResult


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-TCO-CTX",
        scenario_id="S-TCO-CTX",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-TCO-CTX",
        scenario_id="S-TCO-CTX",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-12",
    )


def _tco_result(**overrides) -> TCOResult:
    values = {
        "decision_id": "D-TCO-CTX",
        "scenario_id": "S-TCO-CTX",
        "currency": "EUR",
        "value": Decimal("50"),
        "contributing_components": ("ACQUISITION",),
        "unresolved_components": (),
        "limitations": (),
    }
    values.update(overrides)
    return TCOResult(**values)


def test_matching_complete_tco_context_executes_without_mutation():
    context = _context()
    result = _tco_result()
    context_before = context.model_dump()
    result_before = result.model_dump()

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=context,
        policy_version="MVP-TCO-CTX-1",
        tco_result=result,
    )

    assert outcome.status == BoundaryStatus.COMPLETED
    assert tuple(item.capability for item in outcome.capability_results) == ("TCO",)
    assert outcome.capability_results[0].result_available is True
    assert context.model_dump() == context_before
    assert result.model_dump() == result_before


def test_matching_incomplete_tco_preserves_partial_semantics():
    result = _tco_result(
        value=None,
        unresolved_components=("TRANSPORT",),
        limitations=("MISSING_AMOUNT:TRANSPORT",),
    )

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-TCO-CTX-1",
        tco_result=result,
    )

    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("TRANSPORT",)
    assert outcome.capability_results[0].capability == "TCO"
    assert outcome.capability_results[0].result_available is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "D-OTHER"),
        ("scenario_id", "S-OTHER"),
    ),
)
def test_tco_context_mismatch_is_rejected(field: str, value: str):
    result = _tco_result(**{field: value})

    with pytest.raises(ValueError, match=field):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-TCO-CTX-1",
            tco_result=result,
        )


def test_tco_context_mismatch_reports_all_incompatible_fields():
    result = _tco_result(decision_id="D-OTHER", scenario_id="S-OTHER")

    with pytest.raises(ValueError) as exc_info:
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-TCO-CTX-1",
            tco_result=result,
        )

    message = str(exc_info.value)
    assert "decision_id" in message
    assert "scenario_id" in message


def test_tco_context_mismatch_fails_before_any_capability_runs():
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
            policy_version="MVP-TCO-CTX-1",
            rules_invoker=c0_invoker,
            tco_result=_tco_result(decision_id="D-OTHER"),
        )

    assert calls == []
