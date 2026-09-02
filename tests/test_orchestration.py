from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.orchestration import (
    CapabilityExecution,
    O1ExecutionStatus,
    build_execution_context,
    build_support_package,
)


def context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-001",
        scenario_id="S-001",
        rules_version="R-1",
        parameters_version="P-1",
        data_snapshot_id="DS-1",
    )


def purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-001",
        scenario_id="S-001",
        article_id="A-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5.00"),
        operation_date=date(2026, 9, 1),
    )


def test_execution_context_is_deterministic_and_preserves_versions():
    first = build_execution_context(context())
    second = build_execution_context(context())

    assert first == second
    assert first.decision_id == "D-001"
    assert first.scenario_id == "S-001"
    assert first.rules_version == "R-1"
    assert first.parameters_version == "P-1"
    assert first.data_snapshot_id == "DS-1"


def test_completed_package_requires_completed_capabilities():
    result = CapabilityExecution(
        capability="C0",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=("trace-c0",),
    )

    package = build_support_package(purchase(), context(), (result,))

    assert package.execution_status == O1ExecutionStatus.COMPLETED
    assert package.trace_references == ("trace-c0",)
    assert package.unresolved_items == ()


def test_partial_execution_is_explicit_and_never_false():
    result = CapabilityExecution(
        capability="TCO",
        status=O1ExecutionStatus.NOT_EVALUABLE,
        result_available=False,
        unresolved_items=("TCO_INPUT",),
    )

    package = build_support_package(purchase(), context(), (result,))

    assert package.execution_status == O1ExecutionStatus.PARTIALLY_COMPLETED
    assert package.unresolved_items == ("TCO_INPUT",)
    assert result.result_available is False


def test_failed_capability_requires_reason():
    with pytest.raises(ValueError):
        CapabilityExecution(
            capability="PRICE",
            status=O1ExecutionStatus.FAILED,
            result_available=False,
        )


def test_context_identity_mismatch_is_rejected():
    bad_purchase = purchase().model_copy(update={"decision_id": "D-999"})

    with pytest.raises(ValueError, match="decision_id"):
        build_support_package(bad_purchase, context())


def test_completed_package_cannot_hide_unresolved_items():
    result = CapabilityExecution(
        capability="C0",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        unresolved_items=(),
    )

    package = build_support_package(purchase(), context(), (result,))
    assert package.execution_status == O1ExecutionStatus.COMPLETED


def test_composition_preserves_capability_boundaries():
    c0 = CapabilityExecution(
        capability="C0",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=("trace-c0",),
    )
    price = CapabilityExecution(
        capability="PRICE",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=("trace-price",),
    )
    tco = CapabilityExecution(
        capability="TCO",
        status=O1ExecutionStatus.PARTIALLY_COMPLETED,
        result_available=False,
        unresolved_items=("TRANSPORT",),
    )

    package = build_support_package(purchase(), context(), (c0, price, tco))

    assert package.execution_status == O1ExecutionStatus.PARTIALLY_COMPLETED
    assert package.capability_results == (c0, price, tco)
    assert package.trace_references == ("trace-c0", "trace-price")
    assert package.unresolved_items == ("TRANSPORT",)
    assert package.execution_context.rules_version == "R-1"
    assert package.version_context == ("R-1", "P-1", "DS-1")
