from decimal import Decimal

import pytest

from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.quality.gate import QualityTrustResult
from eios.tco.models import TCOResult


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


def _completed_c0(*_):
    return CapabilityExecution(
        capability="C0",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=("trace-c0",),
    )


def test_mvp_execution_runs_available_capabilities_in_canonical_order():
    quality = QualityTrustResult(status="APTO", confidence="ALTA", checks=())
    tco = TCOResult(
        decision_id="D-MVP",
        scenario_id="S-MVP",
        currency="EUR",
        value=Decimal("55"),
        contributing_components=("purchase",),
        unresolved_components=(),
        limitations=(),
    )

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-1",
        quality_result=quality,
        tco_result=tco,
        rules_invoker=_completed_c0,
    )

    assert outcome.status == BoundaryStatus.COMPLETED
    assert tuple(item.capability for item in outcome.capability_results) == (
        "QTG",
        "TCO",
        "C0",
    )
    assert all(item.result_available for item in outcome.capability_results)


def test_mvp_execution_preserves_partial_tco_state():
    tco = TCOResult(
        decision_id="D-MVP",
        scenario_id="S-MVP",
        currency="EUR",
        value=None,
        contributing_components=("purchase",),
        unresolved_components=("TRANSPORT",),
        limitations=("TRANSPORT_NOT_EVIDENCED",),
    )

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-1",
        tco_result=tco,
    )

    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("TRANSPORT",)
    assert outcome.capability_results[0].capability == "TCO"
    assert outcome.capability_results[0].result_available is False


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
