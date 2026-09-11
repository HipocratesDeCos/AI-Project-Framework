"""Pure deterministic engine for the EIOS delivery/stockout factual analyzer."""
from __future__ import annotations

from collections.abc import Iterable

from .models import (
    DeliveryAnalysisState,
    DeliveryLimitationCode,
    DeliveryStockoutAnalysisInput,
    DeliveryStockoutAnalysisResult,
)


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _context_matches(payload: DeliveryStockoutAnalysisInput) -> bool:
    baseline = payload.baseline
    delivery = payload.delivery
    return all(
        (
            payload.decision_id == baseline.decision_id,
            payload.decision_id == delivery.decision_id,
            payload.article_id == baseline.article_id,
            payload.article_id == delivery.article_id,
            payload.evaluation_date == baseline.evaluation_date,
            payload.evaluation_date == delivery.evaluation_date,
            payload.evaluated_purchase_ref == baseline.evaluated_purchase_ref,
            payload.evaluated_purchase_ref == delivery.evaluated_purchase_ref,
        )
    )


def _result(
    payload: DeliveryStockoutAnalysisInput,
    state: DeliveryAnalysisState,
    limitation_codes: tuple[DeliveryLimitationCode, ...] = (),
) -> DeliveryStockoutAnalysisResult:
    baseline = payload.baseline
    delivery = payload.delivery
    projection = baseline.projection
    projection_issue_refs = tuple(issue.issue_record_ref for issue in projection.issue_refs)
    return DeliveryStockoutAnalysisResult(
        decision_id=payload.decision_id,
        article_id=payload.article_id,
        evaluation_date=payload.evaluation_date,
        evaluated_purchase_ref=payload.evaluated_purchase_ref,
        supplier_id=delivery.supplier_id,
        baseline_projection_ref=baseline.baseline_projection_ref,
        state=state,
        depletion_date=projection.depletion_date.value,
        expected_delivery_date=delivery.expected_delivery_date,
        horizon_end=projection.horizon.horizon_end,
        limitation_codes=tuple(dict.fromkeys(limitation_codes)),
        evidence_refs=_unique((*baseline.evidence_refs, *delivery.evidence_refs)),
        unresolved_refs=_unique(baseline.unresolved_refs),
        issue_refs=_unique((*baseline.issue_refs, *delivery.issue_refs, *projection_issue_refs)),
        trace_refs=_unique((*baseline.trace_refs, *delivery.trace_refs, *projection.trace_refs)),
        upstream_limitations=_unique(baseline.limitations),
    )


def analyze_delivery_stockout(payload: DeliveryStockoutAnalysisInput) -> DeliveryStockoutAnalysisResult:
    """Evaluate the factual temporal relation without producing a rule Assessment."""
    baseline = payload.baseline
    delivery = payload.delivery
    projection = baseline.projection

    if not _context_matches(payload):
        return _result(payload, "NOT_DETERMINABLE")

    if baseline.state == "CONFLICTING_DATA":
        return _result(payload, "CONFLICTING_DATA")
    if baseline.state == "NOT_DETERMINABLE":
        return _result(payload, "NOT_DETERMINABLE")

    if delivery.state == "NOT_EVIDENCED":
        return _result(payload, "NOT_EVIDENCED")
    if delivery.state == "CONFLICTING_DATA":
        return _result(payload, "CONFLICTING_DATA")
    if delivery.state == "NOT_DETERMINABLE":
        if delivery.expected_delivery_date is not None and delivery.expected_delivery_date < delivery.evaluation_date:
            return _result(payload, "NOT_DETERMINABLE", ("PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN",))
        return _result(payload, "NOT_DETERMINABLE")

    depletion = projection.depletion_date
    if depletion.state == "CONFLICTING_DATA":
        return _result(payload, "CONFLICTING_DATA")
    if depletion.state in {"UNKNOWN", "NOT_EVIDENCED"}:
        return _result(payload, "NOT_DETERMINABLE")

    assert delivery.expected_delivery_date is not None

    if depletion.state == "KNOWN":
        assert depletion.value is not None
        if delivery.expected_delivery_date > depletion.value:
            return _result(payload, "LATE_DELIVERY_DEMONSTRATED")
        if delivery.expected_delivery_date < depletion.value:
            return _result(payload, "NOT_LATE_DEMONSTRATED")
        return _result(payload, "NOT_LATE_DEMONSTRATED", ("SAME_DAY_ORDER_NOT_DEMONSTRATED",))

    if depletion.state == "NOT_APPLICABLE":
        horizon = projection.horizon
        if horizon.state != "KNOWN" or horizon.horizon_end is None:
            return _result(payload, "NOT_DETERMINABLE")
        if delivery.expected_delivery_date <= horizon.horizon_end:
            return _result(payload, "NOT_LATE_WITHIN_EVIDENCED_HORIZON")
        return _result(payload, "NOT_DETERMINABLE", ("DELIVERY_BEYOND_STK_HORIZON",))

    return _result(payload, "NOT_DETERMINABLE")


__all__ = ["analyze_delivery_stockout"]
