from datetime import date
from decimal import Decimal
from inspect import signature

import pytest

from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.orchestration import O1ExecutionStatus
from eios.core.tco_integration import build_provenanced_tco_invoker
from eios.tco.models import CostComponent, TCOInput


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
        operation_date=date(2026, 9, 12),
    )


def _complete_payload() -> TCOInput:
    return TCOInput(purchase_operation=_purchase())


def _incomplete_payload() -> TCOInput:
    return TCOInput(
        purchase_operation=_purchase(),
        attributable_costs=(
            CostComponent(
                component="TRANSPORT",
                amount=None,
                currency="EUR",
                applicability="APPLICABLE",
                attribution_ref="ATTR-TRANSPORT",
                rule_reference="RULE-TCO-TRANSPORT",
            ),
        ),
    )


def test_matching_complete_tco_input_executes_through_invoker() -> None:
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-TCO-CTX-1",
        tco_invoker=build_provenanced_tco_invoker(payload=_complete_payload()),
    )

    assert outcome.status == BoundaryStatus.COMPLETED
    capability = outcome.capability_results[0]
    assert capability.capability == "TCO"
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True


def test_matching_incomplete_tco_preserves_partial_semantics() -> None:
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-TCO-CTX-1",
        tco_invoker=build_provenanced_tco_invoker(payload=_incomplete_payload()),
    )

    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("TRANSPORT",)
    capability = outcome.capability_results[0]
    assert capability.capability == "TCO"
    assert capability.status == O1ExecutionStatus.PARTIALLY_COMPLETED
    assert capability.result_available is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("article_id", "ART-OTHER"),
        ("supplier_id", "SUP-OTHER"),
        ("quantity", Decimal("11")),
        ("unit_price", Decimal("6")),
        ("operation_date", date(2026, 9, 11)),
    ),
)
def test_tco_invoker_rejects_foreign_purchase_even_when_ids_match(
    field: str,
    value,
) -> None:
    foreign = _purchase().model_copy(update={field: value})
    invoker = build_provenanced_tco_invoker(payload=_complete_payload())

    with pytest.raises(ValueError, match=field):
        invoker(foreign, _context())


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "D-OTHER"),
        ("scenario_id", "S-OTHER"),
    ),
)
def test_tco_invoker_rejects_foreign_execution_context(
    field: str,
    value: str,
) -> None:
    foreign_context = _context().model_copy(update={field: value})
    invoker = build_provenanced_tco_invoker(payload=_complete_payload())

    with pytest.raises(ValueError, match=field):
        invoker(_purchase(), foreign_context)


def test_tco_invoker_freezes_complete_input_snapshot() -> None:
    payload = _complete_payload()
    invoker = build_provenanced_tco_invoker(payload=payload)

    payload.purchase_operation.quantity = Decimal("999")
    payload.purchase_operation.article_id = "MUTATED-LATER"

    capability = invoker(_purchase(), _context())

    assert capability.capability == "TCO"
    assert capability.status == O1ExecutionStatus.COMPLETED


def test_tco_builder_requires_typed_physical_input() -> None:
    with pytest.raises(TypeError, match="TCOInput"):
        build_provenanced_tco_invoker(payload=object())


def test_mvp_execution_public_signature_has_no_detached_tco_result() -> None:
    parameters = signature(run_mvp_execution).parameters

    assert "tco_result" not in parameters
    assert "tco_invoker" in parameters


def test_old_tco_result_keyword_is_rejected() -> None:
    with pytest.raises(TypeError, match="tco_result"):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-TCO-CTX-1",
            tco_result=object(),
        )
