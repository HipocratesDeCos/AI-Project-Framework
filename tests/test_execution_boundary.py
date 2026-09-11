from datetime import date
from decimal import Decimal

import pytest

from eios.core.execution_boundary import (
    BoundaryStatus,
    ExecutionBoundaryError,
    ExecutionOutcome,
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


def test_non_callable_invoker_is_blocked_before_execution():
    called = []
    plan = ExecutionPlan(capabilities=("C0", "PRICE"), policy_version="E2E-1")
    outcome = execute_plan(
        purchase(), context(), plan,
        {"C0": lambda *_: called.append(1), "PRICE": object()},
    )
    assert outcome.status == BoundaryStatus.BLOCKED
    assert outcome.unresolved_items == ("PRICE:INVALID_INVOKER",)
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
    assert [r.trace_references for r in outcome.capability_results] == [
        ("trace-PRICE",), ("trace-C0",)
    ]


def test_technical_exception_is_failed_not_business_negative():
    plan = ExecutionPlan(capabilities=("PRICE",), policy_version="E2E-1")
    outcome = execute_plan(purchase(), context(), plan, {"PRICE": lambda *_: 1 / 0})
    assert outcome.status == BoundaryStatus.FAILED
    assert outcome.policy_version == "E2E-1"
    assert "PRICE" in outcome.failure_reason


def test_returned_failed_capability_preserves_failure_reason():
    failed = CapabilityExecution(
        capability="PRICE",
        status=O1ExecutionStatus.FAILED,
        result_available=False,
        failure_reason="upstream timeout",
    )
    outcome = execute_plan(
        purchase(), context(),
        ExecutionPlan(capabilities=("PRICE",), policy_version="E2E-1"),
        {"PRICE": lambda *_: failed},
    )
    assert outcome.status == BoundaryStatus.FAILED
    assert outcome.failure_reason == "PRICE: upstream timeout"
    assert outcome.capability_results == (failed,)


def test_identity_mismatch_is_rejected():
    bad = purchase().model_copy(update={"scenario_id": "S-9"})
    with pytest.raises(ExecutionBoundaryError, match="scenario_id"):
        execute_plan(
            bad, context(),
            ExecutionPlan(capabilities=("C0",), policy_version="E2E-1"),
            {"C0": completed},
        )


def test_decision_identity_mismatch_is_rejected():
    bad = purchase().model_copy(update={"decision_id": "D-9"})
    with pytest.raises(ExecutionBoundaryError, match="decision_id"):
        execute_plan(
            bad, context(),
            ExecutionPlan(capabilities=("C0",), policy_version="E2E-1"),
            {"C0": completed},
        )


def test_partial_capability_remains_partial():
    plan = ExecutionPlan(capabilities=("TCO",), policy_version="E2E-1")
    result = CapabilityExecution(
        capability="TCO", status=O1ExecutionStatus.NOT_EVALUABLE,
        result_available=False, unresolved_items=("TRANSPORT",)
    )
    outcome = execute_plan(purchase(), context(), plan, {"TCO": lambda *_: result})
    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("TRANSPORT",)


@pytest.mark.parametrize("capability_status", [O1ExecutionStatus.READY, O1ExecutionStatus.RUNNING])
def test_nonterminal_capability_state_remains_partial(capability_status):
    result = CapabilityExecution(
        capability="PRICE",
        status=capability_status,
        result_available=False,
    )
    outcome = execute_plan(
        purchase(), context(),
        ExecutionPlan(capabilities=("PRICE",), policy_version="E2E-1"),
        {"PRICE": lambda *_: result},
    )
    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.capability_results == (result,)


def test_completed_capability_without_result_is_failed():
    incomplete = CapabilityExecution(
        capability="PRICE",
        status=O1ExecutionStatus.COMPLETED,
        result_available=False,
    )
    outcome = execute_plan(
        purchase(), context(),
        ExecutionPlan(capabilities=("PRICE",), policy_version="E2E-1"),
        {"PRICE": lambda *_: incomplete},
    )
    assert outcome.status == BoundaryStatus.FAILED
    assert "COMPLETED" in outcome.failure_reason
    assert "resultado" in outcome.failure_reason


def test_invoker_cannot_mutate_input_seen_by_later_capabilities_or_caller():
    original_purchase = purchase()
    original_context = context()
    seen = []

    def mutator(purchase_arg, context_arg):
        purchase_arg.scenario_id = "MUTATED"
        context_arg.rules_version = "MUTATED"
        return completed("FIRST")

    def observer(purchase_arg, context_arg):
        seen.append((purchase_arg.scenario_id, context_arg.rules_version))
        return completed("SECOND")

    outcome = execute_plan(
        original_purchase,
        original_context,
        ExecutionPlan(capabilities=("FIRST", "SECOND"), policy_version="E2E-1"),
        {"FIRST": mutator, "SECOND": observer},
    )
    assert outcome.status == BoundaryStatus.COMPLETED
    assert seen == [("S-1", "R-1")]
    assert original_purchase.scenario_id == "S-1"
    assert original_context.rules_version == "R-1"


def test_catalog_snapshot_is_stable_during_execution():
    catalog = {}

    def first(*_):
        catalog["SECOND"] = lambda *_: completed("WRONG")
        return completed("FIRST")

    def second(*_):
        return completed("SECOND")

    catalog.update({"FIRST": first, "SECOND": second})
    outcome = execute_plan(
        purchase(), context(),
        ExecutionPlan(capabilities=("FIRST", "SECOND"), policy_version="E2E-1"),
        catalog,
    )
    assert outcome.status == BoundaryStatus.COMPLETED
    assert [item.capability for item in outcome.capability_results] == ["FIRST", "SECOND"]


def test_capability_identity_mismatch_fails_explicitly():
    outcome = execute_plan(
        purchase(), context(),
        ExecutionPlan(capabilities=("PRICE",), policy_version="E2E-1"),
        {"PRICE": lambda *_: completed("TCO")},
    )
    assert outcome.status == BoundaryStatus.FAILED
    assert "PRICE" in outcome.failure_reason
    assert "TCO" in outcome.failure_reason


def test_context_versions_are_passed_unchanged():
    captured = []

    def invoker(_, context_arg):
        captured.append(
            (
                context_arg.rules_version,
                context_arg.parameters_version,
                context_arg.data_snapshot_id,
            )
        )
        return completed("C0")

    outcome = execute_plan(
        purchase(), context(),
        ExecutionPlan(capabilities=("C0",), policy_version="E2E-1"),
        {"C0": invoker},
    )
    assert outcome.status == BoundaryStatus.COMPLETED
    assert captured == [("R-1", "P-1", "DS-1")]


def test_plan_and_inputs_are_not_mutated():
    plan = ExecutionPlan(capabilities=("C0",), policy_version="E2E-1")
    invokers = {"C0": completed}
    original_purchase = purchase()
    original_context = context()
    before_plan = plan.model_dump()
    before_purchase = original_purchase.model_dump()
    before_context = original_context.model_dump()
    execute_plan(original_purchase, original_context, plan, invokers)
    assert plan.model_dump() == before_plan
    assert original_purchase.model_dump() == before_purchase
    assert original_context.model_dump() == before_context


@pytest.mark.parametrize(
    "status",
    [BoundaryStatus.READY, BoundaryStatus.RUNNING, BoundaryStatus.NOT_EVALUABLE],
)
def test_synchronous_outcome_rejects_non_terminal_statuses(status):
    with pytest.raises(ValueError, match="terminal"):
        ExecutionOutcome(status=status, policy_version="E2E-1")


def test_failed_outcome_requires_reason():
    with pytest.raises(ValueError, match="failure_reason"):
        ExecutionOutcome(status=BoundaryStatus.FAILED, policy_version="E2E-1")


def test_completed_outcome_rejects_unresolved_items():
    with pytest.raises(ValueError, match="unresolved_items"):
        ExecutionOutcome(
            status=BoundaryStatus.COMPLETED,
            policy_version="E2E-1",
            unresolved_items=("x",),
        )


def test_execution_outcome_is_immutable():
    outcome = execute_plan(
        purchase(), context(),
        ExecutionPlan(capabilities=("C0",), policy_version="E2E-1"),
        {"C0": completed},
    )
    with pytest.raises((TypeError, ValueError)):
        outcome.status = BoundaryStatus.FAILED


@pytest.mark.parametrize(
    "forbidden",
    ["score", "ranking", "winner", "selected_alternative", "recommendation", "business_decision"],
)
def test_forbidden_business_outputs_are_absent(forbidden):
    outcome = execute_plan(
        purchase(), context(),
        ExecutionPlan(capabilities=("C0",), policy_version="E2E-1"),
        {"C0": completed},
    )
    assert not hasattr(outcome, forbidden)
