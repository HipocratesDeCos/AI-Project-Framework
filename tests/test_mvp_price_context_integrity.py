from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.pricing.models import PriceCounts, PriceIntelligenceResult


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-PRICE-CTX",
        scenario_id="S-PRICE-CTX",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-PRICE-CTX",
        scenario_id="S-PRICE-CTX",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-12",
    )


def _price_result() -> PriceIntelligenceResult:
    return PriceIntelligenceResult(
        decision_id="D-PRICE-CTX",
        scenario_id="S-PRICE-CTX",
        data_snapshot_id="snapshot-v1",
        methodology_version="price-v1",
        pr_value=Decimal("5.0000"),
        currency="EUR",
        sufficiency_status="SUFFICIENT",
        pr_status="PR_AVAILABLE",
        pr_limitations=(),
        reference_set=("REF-1", "REF-2"),
        counts=PriceCounts(
            n_raw=2,
            n_unique=2,
            n_comparable=2,
            n_representative=2,
            n_selected=2,
        ),
        aggregation_method="MEDIAN_UNWEIGHTED",
        trace_references=("trace-price",),
    )


def test_matching_price_context_executes_without_mutation():
    context = _context()
    result = _price_result()
    context_before = context.model_dump()
    result_before = result.model_dump()

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=context,
        policy_version="MVP-PRICE-CTX-1",
        price_result=result,
    )

    assert tuple(item.capability for item in outcome.capability_results) == ("PRICE",)
    assert outcome.capability_results[0].result_available is True
    assert context.model_dump() == context_before
    assert result.model_dump() == result_before


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "D-OTHER"),
        ("scenario_id", "S-OTHER"),
        ("data_snapshot_id", "snapshot-other"),
    ),
)
def test_price_context_mismatch_is_rejected(field: str, value: str):
    result = _price_result().model_copy(update={field: value})

    with pytest.raises(ValueError, match=field):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-PRICE-CTX-1",
            price_result=result,
        )


def test_price_context_mismatch_fails_before_any_capability_runs():
    calls: list[str] = []

    def c0_invoker(*_):
        calls.append("C0")
        return CapabilityExecution(
            capability="C0",
            status=O1ExecutionStatus.COMPLETED,
            result_available=True,
        )

    result = _price_result().model_copy(
        update={
            "decision_id": "D-OTHER",
            "scenario_id": "S-OTHER",
            "data_snapshot_id": "snapshot-other",
        }
    )

    with pytest.raises(ValueError) as exc_info:
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-PRICE-CTX-1",
            price_result=result,
            rules_invoker=c0_invoker,
        )

    message = str(exc_info.value)
    assert "decision_id" in message
    assert "scenario_id" in message
    assert "data_snapshot_id" in message
    assert calls == []
