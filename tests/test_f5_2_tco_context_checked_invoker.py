"""F5.2: strict, opt-in context binding for the EXISTING TCO producer.

Only the new TCO adapter is changed. The old entry point remains unchanged;
neither the TCO engine nor the neutral kernel gains any business authority.
"""
from datetime import date
from decimal import Decimal

import pytest

from eios.core import tco_integration
from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.orchestration import O1ExecutionStatus
from eios.core.tco_integration import (
    build_context_checked_tco_invoker,
    build_provenanced_tco_invoker,
)
from eios.tco.engine import calculate_tco
from eios.tco.models import CostComponent, TCOInput


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-F5-2", scenario_id="S-F5-2",
        rules_version="RULES-1", parameters_version="PARAMS-1",
        data_snapshot_id="SYNTHETIC-SNAPSHOT-1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-F5-2", scenario_id="S-F5-2",
        article_id="SYNTH-ARTICLE", supplier_id="SYNTH-SUPPLIER",
        quantity=Decimal("10"), unit_price=Decimal("5"),
        currency="EUR", operation_date=date(2026, 10, 1),
    )


def _payload(*, incomplete: bool = False) -> TCOInput:
    if incomplete:
        return TCOInput(
            purchase_operation=_purchase(),
            attributable_costs=(
                CostComponent(
                    component="TRANSPORT", amount=None, currency="EUR",
                    applicability="APPLICABLE", attribution_ref="SYNTHETIC-TRANSPORT",
                    rule_reference="RULE-TCO-TRANSPORT",
                ),
            ),
        )
    return TCOInput(purchase_operation=_purchase())


def test_strict_context_check_preserves_completed_tco_and_legacy_calculation():
    expected = calculate_tco(_payload())
    assert expected.complete is True
    assert expected.value == Decimal("50")
    strict = build_context_checked_tco_invoker(
        payload=_payload(), expected_context=_context(),
    )
    direct = strict(_purchase(), _context())
    old = build_provenanced_tco_invoker(payload=_payload())(
        _purchase(), _context(),
    )
    assert direct == old
    assert direct.status == O1ExecutionStatus.COMPLETED
    assert direct.result_available is True
    outcome = run_mvp_execution(
        purchase=_purchase(), context=_context(),
        policy_version="TCO-CONTEXT-CHECKED-1",
        tco_invoker=strict,
    )
    assert outcome.status == BoundaryStatus.COMPLETED
    assert outcome.capability_results == (direct,)


@pytest.mark.parametrize("field", tuple(DecisionContext.model_fields))
def test_strict_invoker_rejects_any_foreign_context_before_calculation(field, monkeypatch):
    calls = []
    original = tco_integration.calculate_tco

    def counted(payload):
        calls.append("CALCULATED")
        return original(payload)

    monkeypatch.setattr(tco_integration, "calculate_tco", counted)
    strict = build_context_checked_tco_invoker(
        payload=_payload(), expected_context=_context(),
    )
    foreign = _context().model_copy(update={field: "FOREIGN"})
    with pytest.raises(ValueError, match=field):
        strict(_purchase(), foreign)
    assert calls == []


@pytest.mark.parametrize("field", (
    "rules_version", "parameters_version", "data_snapshot_id",
))
def test_version_drift_fails_closed_through_legacy_mvp_execution(field):
    strict = build_context_checked_tco_invoker(
        payload=_payload(), expected_context=_context(),
    )
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context().model_copy(update={field: "OTHER-VERSION"}),
        policy_version="TCO-CONTEXT-CHECKED-1",
        tco_invoker=strict,
    )
    assert outcome.status == BoundaryStatus.FAILED
    assert outcome.capability_results == ()
    assert outcome.failure_reason.startswith("TCO:")
    assert field in outcome.failure_reason


@pytest.mark.parametrize("field", ("decision_id", "scenario_id"))
def test_builder_rejects_inconsistent_expected_context_even_before_invocation(field):
    foreign = _context().model_copy(update={field: "FOREIGN"})
    with pytest.raises(ValueError, match=field):
        build_context_checked_tco_invoker(
            payload=_payload(), expected_context=foreign,
        )


def test_builder_requires_typed_frozen_inputs():
    with pytest.raises(TypeError, match="DecisionContext"):
        build_context_checked_tco_invoker(
            payload=_payload(), expected_context=object(),
        )
    with pytest.raises(TypeError, match="TCOInput"):
        build_context_checked_tco_invoker(
            payload=object(), expected_context=_context(),
        )

    original_payload = _payload()
    original_context = _context()
    strict = build_context_checked_tco_invoker(
        payload=original_payload, expected_context=original_context,
    )
    original_context.parameters_version = "CORRUPTED_LATER"
    original_payload.purchase_operation.quantity = Decimal("999")
    direct = strict(_purchase(), _context())
    assert direct.status == O1ExecutionStatus.COMPLETED


@pytest.mark.parametrize("field,value", (
    ("supplier_id", "OTHER-SUPPLIER"),
    ("article_id", "OTHER-ARTICLE"),
    ("quantity", Decimal("100")),
    ("unit_price", Decimal("500")),
))
def test_strict_adapter_still_rejects_foreign_purchase(field, value):
    strict = build_context_checked_tco_invoker(
        payload=_payload(), expected_context=_context(),
    )
    foreign = _purchase().model_copy(update={field: value})
    with pytest.raises(ValueError, match=field):
        strict(foreign, _context())


def test_strict_context_check_does_not_hide_incomplete_tco():
    strict = build_context_checked_tco_invoker(
        payload=_payload(incomplete=True), expected_context=_context(),
    )
    observed = strict(_purchase(), _context())
    assert observed.capability == "TCO"
    assert observed.status == O1ExecutionStatus.PARTIALLY_COMPLETED
    assert observed.result_available is False
    assert observed.unresolved_items == ("TRANSPORT",)


def test_legacy_public_builder_retained_for_compatibility():
    legacy = build_provenanced_tco_invoker(payload=_payload())
    result = legacy(_purchase(), _context())
    assert result.capability == "TCO"
    assert result.status == O1ExecutionStatus.COMPLETED
