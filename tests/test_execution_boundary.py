from datetime import date
from decimal import Decimal

import pytest

from eios.core.execution_boundary import (
    BoundaryStatus,
    ExecutionBoundaryError,
    ExecutionPlan,
    execute_plan,
)
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus


def context():
    return DecisionContext(
        decision_id="D-1", scenario_id="S-1", rules_version="R-1",
        parameters_version="P-1", data_snapshot_id="DS-1"
    )


def purchase():
    return PurchaseOperation(
        decision_id="D-1", scenario_id="S-1", article_id="A-1",
        supplier_id="SUP-1", quantity=Decimal("2"), unit_price=Decimal("5"),
        operation_date=date(2026, 9, 3)
    )


def completed(name):
    return CapabilityExecution(
        capability=name, status=O1ExecutionStatus.COMPLETED,
        result_available=True, trace_references=(f"trace-{name}",)
    )


def test_plan_requires_unique_capabilities():
    with pytest.raises(ValueError):
        ExecutionPlan(capabilities=("C0", "C0"), policy_version="E2E-1")


def test_plan_requires_policy_version():
    with pytest.raises(ValueError):
        ExecutionPlan(capabilities=("C0",), policy_version="")


def test_unknown_capability_is_blocked_before_execution():
    called = []
    plan = ExecutionPlan(capabilities=("C0", "PRICE"), policy_version="E2E-1")
    outcome = execute_plan(purchase(), context(), plan, {"C0": lambda *_: called.append(1)})
    assert outcome.status == BoundaryStatus.BLOCKED
    assert outcome.policy_version == "E2E-1"
    assert called == []


def test_declared_plan_executes_in_declared_order():
    order = []
    plan = ExecutionPlan(capabilities=("PRICE", "C0"), policy_version="E2E-1")
    invokers = {
        "PRICE": lambda *_: (order.append("PRICE") or completed("PRICE")),
        "C0": lambda *_: (order.append("C0") or completed("C0")),
    }
    outcome = execute_plan(purchase(), context(), plan, invokers)
    assert outcome.status == BoundaryStatus.COMPLETED
    assert outcome.policy_version == "E2E-1"
    assert order == ["PRICE", "C0"]
    assert [r.capability for r in outcome.capability_results] == ["PRICE", "C0"]


def test_technical_exception_is_failed_not_business_negative():
    plan = ExecutionPlan(capabilities=("PRICE",), policy_version="E2E-1")
    outcome = execute_plan(purchase(), context(), plan, {"PRICE": lambda *_: 1 / 0})
    assert outcome.status == BoundaryStatus.FAILED
    assert outcome.policy_version == "E2E-1"
    assert "PRICE" in outcome.failure_reason


def test_identity_mismatch_is_rejected():
    bad = purchase().model_copy(update={"scenario_id": "S-9"})
    with pytest.raises(ExecutionBoundaryError, match="scenario_id"):
        execute_plan(bad, context(), ExecutionPlan(capabilities=("C0",), policy_version="E2E-1"), {"C0": completed})


def test_partial_capability_remains_partial():
    plan = ExecutionPlan(capabilities=("TCO",), policy_version="E2E-1")
    result = CapabilityExecution(
        capability="TCO", status=O1ExecutionStatus.NOT_EVALUABLE,
        result_available=False, unresolved_items=("TRANSPORT",)
    )
    outcome = execute_plan(purchase(), context(), plan, {"TCO": lambda *_: result})
    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("TRANSPORT",)


def test_plan_and_inputs_are_not_mutated():
    plan = ExecutionPlan(capabilities=("C0",), policy_version="E2E-1")
    invokers = {"C0": completed}
    before_plan = plan.model_dump()
    before_purchase = purchase().model_dump()
    before_context = context().model_dump()
    execute_plan(purchase(), context(), plan, invokers)
    assert plan.model_dump() == before_plan
    assert purchase().model_dump() == before_purchase
    assert context().model_dump() == before_context


def test_execution_outcome_is_immutable():
    outcome = execute_plan(
        purchase(), context(),
        ExecutionPlan(capabilities=("C0",), policy_version="E2E-1"),
        {"C0": completed},
    )
    with pytest.raises((TypeError, ValueError)):
        outcome.status = BoundaryStatus.FAILED
