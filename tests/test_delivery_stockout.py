from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.delivery import (
    BaselineStockoutQualification,
    DeliveryStockoutAnalysisInput,
    PurchaseSpecificDeliveryTimingEvidence,
    analyze_delivery_stockout,
)
from eios.stock.models import (
    ConfiguredParameterValue,
    DataIssueRef,
    ProjectedDateMetric,
    ProjectedDecimalMetric,
    ProjectionHorizon,
    StockProjectionResult,
    StockResultIdentity,
)


EVALUATION_DATE = date(2026, 9, 11)
DECISION_ID = "DEC-ENT-001"
ARTICLE_ID = "ART-001"
SUPPLIER_ID = "SUP-001"
PURCHASE_REF = "purchase-proposal:001"
PARAMETERS_VERSION = "params-v1"


def _identity(
    *,
    decision_id: str = DECISION_ID,
    article_id: str = ARTICLE_ID,
    evaluation_date: date = EVALUATION_DATE,
) -> StockResultIdentity:
    return StockResultIdentity(
        decision_id=decision_id,
        scenario_id="SCN-BASE",
        rules_version="rules-v1",
        parameters_version=PARAMETERS_VERSION,
        data_snapshot_id="snapshot-v1",
        company_id="COMP-1",
        operational_scope_id="OPS-1",
        article_id=article_id,
        evaluation_date=evaluation_date,
        base_unit="unit",
        methodology_version="0.1",
    )


def _horizon(*, state: str = "KNOWN", evaluation_date: date = EVALUATION_DATE) -> ProjectionHorizon:
    if state == "KNOWN":
        parameter = ConfiguredParameterValue(
            parameter_id="PYE-001",
            company_id="COMP-1",
            value=30,
            unit="day",
            state="KNOWN",
            parameters_version=PARAMETERS_VERSION,
            applicable_reference_date=evaluation_date,
            configuration_ref="cfg:pye-001",
            source_ref="source:pye-001",
        )
        return ProjectionHorizon(
            parameter=parameter,
            horizon_days=30,
            horizon_end=evaluation_date + timedelta(days=30),
            state="KNOWN",
        )
    parameter = ConfiguredParameterValue(
        parameter_id="PYE-001",
        company_id="COMP-1",
        state=state,
        parameters_version=PARAMETERS_VERSION,
        applicable_reference_date=evaluation_date,
    )
    return ProjectionHorizon(parameter=parameter, state=state)


def _contradiction(prefix: str = "stk") -> DataIssueRef:
    return DataIssueRef(
        issue_id=f"{prefix}-contradiction",
        issue_type="CONTRADICTION",
        issue_record_ref=f"issue-record:{prefix}",
        evidence_refs=(f"{prefix}-e1", f"{prefix}-e2"),
    )


def _projection(
    *,
    depletion_state: str = "KNOWN",
    depletion_date: date | None = EVALUATION_DATE + timedelta(days=10),
    horizon_state: str = "KNOWN",
    decision_id: str = DECISION_ID,
    article_id: str = ARTICLE_ID,
    evaluation_date: date = EVALUATION_DATE,
    issue: DataIssueRef | None = None,
) -> StockProjectionResult:
    horizon = _horizon(state=horizon_state, evaluation_date=evaluation_date)
    if depletion_state == "KNOWN":
        depletion = ProjectedDateMetric(value=depletion_date, state="KNOWN", trace_refs=("trace:depletion",))
    elif depletion_state == "CONFLICTING_DATA":
        conflict = issue or _contradiction()
        depletion = ProjectedDateMetric(state="CONFLICTING_DATA", issue_refs=(conflict,), trace_refs=("trace:depletion",))
    else:
        depletion = ProjectedDateMetric(state=depletion_state, trace_refs=("trace:depletion",))

    projection_issue_refs = (issue or _contradiction(),) if depletion_state == "CONFLICTING_DATA" else (() if issue is None else (issue,))
    result_state = "KNOWN" if depletion_state in {"KNOWN", "NOT_APPLICABLE"} else depletion_state
    return StockProjectionResult(
        identity=_identity(decision_id=decision_id, article_id=article_id, evaluation_date=evaluation_date),
        horizon=horizon,
        minimum_projected_stock=ProjectedDecimalMetric(value=Decimal("1"), state="KNOWN"),
        depletion_date=depletion,
        state=result_state,
        issue_refs=projection_issue_refs,
        trace_refs=("trace:projection",),
    )


def _baseline(
    *,
    projection: StockProjectionResult | None = None,
    state: str = "KNOWN",
    decision_id: str | None = None,
    article_id: str | None = None,
    evaluation_date: date | None = None,
    purchase_ref: str = PURCHASE_REF,
    limitations: tuple[str, ...] = (),
) -> BaselineStockoutQualification:
    projection = projection or _projection()
    decision_id = decision_id or projection.identity.decision_id
    article_id = article_id or projection.identity.article_id
    evaluation_date = evaluation_date or projection.identity.evaluation_date
    kwargs = dict(
        decision_id=decision_id,
        article_id=article_id,
        evaluation_date=evaluation_date,
        evaluated_purchase_ref=purchase_ref,
        baseline_projection_ref="stock-projection:baseline",
        projection=projection,
        state=state,
        limitations=limitations,
        trace_refs=("trace:baseline",),
    )
    if state == "KNOWN":
        kwargs.update(
            baseline_relation_ref="baseline:relation",
            projection_provenance_ref="baseline:provenance",
            purchase_exclusion_ref="baseline:purchase-excluded",
        )
    elif state == "CONFLICTING_DATA":
        kwargs.update(issue_refs=("issue:baseline-conflict",))
    return BaselineStockoutQualification(**kwargs)


def _delivery(
    *,
    state: str = "KNOWN",
    expected_delivery_date: date | None = EVALUATION_DATE + timedelta(days=12),
    decision_id: str = DECISION_ID,
    article_id: str = ARTICLE_ID,
    evaluation_date: date = EVALUATION_DATE,
    purchase_ref: str = PURCHASE_REF,
    source_ref: str | None = "source:delivery",
) -> PurchaseSpecificDeliveryTimingEvidence:
    kwargs = dict(
        decision_id=decision_id,
        article_id=article_id,
        supplier_id=SUPPLIER_ID,
        evaluation_date=evaluation_date,
        evaluated_purchase_ref=purchase_ref,
        state=state,
        expected_delivery_date=expected_delivery_date,
        source_ref=source_ref,
        trace_refs=("trace:delivery",),
    )
    if state == "KNOWN":
        kwargs.update(
            delivery_semantic_ref="semantic:expected-delivery-date",
            purchase_applicability_ref="applicability:purchase-001",
            evidence_refs=("evidence:delivery",),
            captured_at=EVALUATION_DATE,
        )
    elif state == "CONFLICTING_DATA":
        kwargs.update(expected_delivery_date=None, issue_refs=("issue:delivery-conflict",))
    elif state == "NOT_DETERMINABLE" and expected_delivery_date is not None:
        kwargs.update(
            delivery_semantic_ref="semantic:expected-delivery-date",
            evidence_refs=("evidence:delivery",),
            captured_at=EVALUATION_DATE,
            purchase_applicability_ref=None,
        )
    return PurchaseSpecificDeliveryTimingEvidence(**kwargs)


def _payload(
    *,
    baseline: BaselineStockoutQualification | None = None,
    delivery: PurchaseSpecificDeliveryTimingEvidence | None = None,
    decision_id: str = DECISION_ID,
    article_id: str = ARTICLE_ID,
    evaluation_date: date = EVALUATION_DATE,
    purchase_ref: str = PURCHASE_REF,
) -> DeliveryStockoutAnalysisInput:
    return DeliveryStockoutAnalysisInput(
        decision_id=decision_id,
        article_id=article_id,
        evaluation_date=evaluation_date,
        evaluated_purchase_ref=purchase_ref,
        baseline=baseline or _baseline(),
        delivery=delivery or _delivery(),
    )


def test_delivery_after_depletion_is_late() -> None:
    result = analyze_delivery_stockout(_payload())
    assert result.state == "LATE_DELIVERY_DEMONSTRATED"
    assert result.expected_delivery_date > result.depletion_date


def test_delivery_before_depletion_is_not_late() -> None:
    delivery = _delivery(expected_delivery_date=EVALUATION_DATE + timedelta(days=5))
    result = analyze_delivery_stockout(_payload(delivery=delivery))
    assert result.state == "NOT_LATE_DEMONSTRATED"
    assert result.limitation_codes == ()


def test_same_day_is_not_late_but_preserves_intraday_limitation() -> None:
    same_day = EVALUATION_DATE + timedelta(days=10)
    result = analyze_delivery_stockout(_payload(delivery=_delivery(expected_delivery_date=same_day)))
    assert result.state == "NOT_LATE_DEMONSTRATED"
    assert result.limitation_codes == ("SAME_DAY_ORDER_NOT_DEMONSTRATED",)


def test_not_applicable_depletion_with_delivery_inside_horizon() -> None:
    baseline = _baseline(projection=_projection(depletion_state="NOT_APPLICABLE", depletion_date=None))
    result = analyze_delivery_stockout(_payload(baseline=baseline))
    assert result.state == "NOT_LATE_WITHIN_EVIDENCED_HORIZON"
    assert result.depletion_date is None


def test_not_applicable_depletion_beyond_horizon_is_indeterminate() -> None:
    baseline = _baseline(projection=_projection(depletion_state="NOT_APPLICABLE", depletion_date=None))
    delivery = _delivery(expected_delivery_date=EVALUATION_DATE + timedelta(days=31))
    result = analyze_delivery_stockout(_payload(baseline=baseline, delivery=delivery))
    assert result.state == "NOT_DETERMINABLE"
    assert result.limitation_codes == ("DELIVERY_BEYOND_STK_HORIZON",)


def test_not_applicable_without_known_horizon_is_indeterminate() -> None:
    baseline = _baseline(
        projection=_projection(depletion_state="NOT_APPLICABLE", depletion_date=None, horizon_state="UNKNOWN")
    )
    result = analyze_delivery_stockout(_payload(baseline=baseline))
    assert result.state == "NOT_DETERMINABLE"


@pytest.mark.parametrize("state", ["UNKNOWN", "NOT_EVIDENCED"])
def test_uncertain_depletion_is_indeterminate(state: str) -> None:
    baseline = _baseline(projection=_projection(depletion_state=state, depletion_date=None))
    result = analyze_delivery_stockout(_payload(baseline=baseline))
    assert result.state == "NOT_DETERMINABLE"


def test_conflicting_depletion_is_conflicting() -> None:
    issue = _contradiction("depletion")
    baseline = _baseline(projection=_projection(depletion_state="CONFLICTING_DATA", depletion_date=None, issue=issue))
    result = analyze_delivery_stockout(_payload(baseline=baseline))
    assert result.state == "CONFLICTING_DATA"
    assert "issue-record:depletion" in result.issue_refs


def test_not_evidenced_delivery_preserves_declared_date_but_does_not_compare() -> None:
    declared = EVALUATION_DATE + timedelta(days=40)
    delivery = _delivery(state="NOT_EVIDENCED", expected_delivery_date=declared)
    result = analyze_delivery_stockout(_payload(delivery=delivery))
    assert result.state == "NOT_EVIDENCED"
    assert result.expected_delivery_date == declared
    assert "DELIVERY_BEYOND_STK_HORIZON" not in result.limitation_codes


def test_conflicting_delivery_is_conflicting() -> None:
    result = analyze_delivery_stockout(_payload(delivery=_delivery(state="CONFLICTING_DATA", expected_delivery_date=None)))
    assert result.state == "CONFLICTING_DATA"


def test_indeterminate_past_delivery_marks_applicability_limitation() -> None:
    past = EVALUATION_DATE - timedelta(days=1)
    delivery = _delivery(state="NOT_DETERMINABLE", expected_delivery_date=past)
    result = analyze_delivery_stockout(_payload(delivery=delivery))
    assert result.state == "NOT_DETERMINABLE"
    assert result.limitation_codes == ("PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN",)


def test_indeterminate_future_delivery_has_no_past_limitation() -> None:
    delivery = _delivery(state="NOT_DETERMINABLE", expected_delivery_date=EVALUATION_DATE + timedelta(days=2))
    result = analyze_delivery_stockout(_payload(delivery=delivery))
    assert result.state == "NOT_DETERMINABLE"
    assert result.limitation_codes == ()


def test_past_known_delivery_with_applicability_compares_normally() -> None:
    delivery = _delivery(state="KNOWN", expected_delivery_date=EVALUATION_DATE - timedelta(days=1))
    result = analyze_delivery_stockout(_payload(delivery=delivery))
    assert result.state == "NOT_LATE_DEMONSTRATED"
    assert "PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN" not in result.limitation_codes


def test_baseline_conflict_prevents_temporal_comparison() -> None:
    result = analyze_delivery_stockout(_payload(baseline=_baseline(state="CONFLICTING_DATA")))
    assert result.state == "CONFLICTING_DATA"


def test_baseline_not_determinable_prevents_temporal_comparison() -> None:
    result = analyze_delivery_stockout(_payload(baseline=_baseline(state="NOT_DETERMINABLE")))
    assert result.state == "NOT_DETERMINABLE"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("decision_id", "OTHER-DECISION"),
        ("article_id", "OTHER-ARTICLE"),
        ("evaluation_date", EVALUATION_DATE + timedelta(days=1)),
        ("purchase_ref", "purchase-proposal:other"),
    ],
)
def test_target_context_mismatch_is_not_determinable(field: str, value) -> None:
    kwargs = {field: value}
    result = analyze_delivery_stockout(_payload(**kwargs))
    assert result.state == "NOT_DETERMINABLE"


def test_baseline_internal_identity_mismatch_is_rejected() -> None:
    projection = _projection(decision_id="PROJECTION-DECISION")
    with pytest.raises(ValidationError):
        _baseline(projection=projection, decision_id=DECISION_ID)


def test_known_baseline_requires_exclusion_provenance() -> None:
    projection = _projection()
    with pytest.raises(ValidationError):
        BaselineStockoutQualification(
            decision_id=DECISION_ID,
            article_id=ARTICLE_ID,
            evaluation_date=EVALUATION_DATE,
            evaluated_purchase_ref=PURCHASE_REF,
            baseline_projection_ref="stock-projection:baseline",
            projection=projection,
            state="KNOWN",
            baseline_relation_ref="baseline:relation",
            projection_provenance_ref="baseline:provenance",
            purchase_exclusion_ref=None,
            trace_refs=("trace:baseline",),
        )


def test_known_delivery_requires_purchase_applicability() -> None:
    with pytest.raises(ValidationError):
        PurchaseSpecificDeliveryTimingEvidence(
            decision_id=DECISION_ID,
            article_id=ARTICLE_ID,
            supplier_id=SUPPLIER_ID,
            evaluation_date=EVALUATION_DATE,
            evaluated_purchase_ref=PURCHASE_REF,
            state="KNOWN",
            expected_delivery_date=EVALUATION_DATE + timedelta(days=2),
            delivery_semantic_ref="semantic:delivery",
            source_ref="source:delivery",
            evidence_refs=("evidence:delivery",),
            captured_at=EVALUATION_DATE,
        )


def test_not_evidenced_declared_date_requires_source() -> None:
    with pytest.raises(ValidationError):
        _delivery(state="NOT_EVIDENCED", expected_delivery_date=EVALUATION_DATE + timedelta(days=2), source_ref=None)


def test_conflicting_delivery_cannot_publish_unique_date() -> None:
    with pytest.raises(ValidationError):
        PurchaseSpecificDeliveryTimingEvidence(
            decision_id=DECISION_ID,
            article_id=ARTICLE_ID,
            supplier_id=SUPPLIER_ID,
            evaluation_date=EVALUATION_DATE,
            evaluated_purchase_ref=PURCHASE_REF,
            state="CONFLICTING_DATA",
            expected_delivery_date=EVALUATION_DATE + timedelta(days=2),
            issue_refs=("issue:delivery-conflict",),
        )


def test_invalid_validity_interval_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PurchaseSpecificDeliveryTimingEvidence(
            decision_id=DECISION_ID,
            article_id=ARTICLE_ID,
            supplier_id=SUPPLIER_ID,
            evaluation_date=EVALUATION_DATE,
            evaluated_purchase_ref=PURCHASE_REF,
            state="NOT_EVIDENCED",
            valid_from=EVALUATION_DATE + timedelta(days=2),
            valid_to=EVALUATION_DATE + timedelta(days=1),
        )


def test_indeterminate_date_form_cannot_claim_purchase_applicability() -> None:
    with pytest.raises(ValidationError):
        PurchaseSpecificDeliveryTimingEvidence(
            decision_id=DECISION_ID,
            article_id=ARTICLE_ID,
            supplier_id=SUPPLIER_ID,
            evaluation_date=EVALUATION_DATE,
            evaluated_purchase_ref=PURCHASE_REF,
            state="NOT_DETERMINABLE",
            expected_delivery_date=EVALUATION_DATE - timedelta(days=1),
            delivery_semantic_ref="semantic:delivery",
            purchase_applicability_ref="applicability:claimed",
            source_ref="source:delivery",
            evidence_refs=("evidence:delivery",),
            captured_at=EVALUATION_DATE,
        )


def test_projection_issue_record_ref_is_preserved_without_serializing_issue() -> None:
    issue = DataIssueRef(
        issue_id="missing-1",
        issue_type="MISSING_DATA",
        issue_record_ref="issue-record:missing-1",
    )
    baseline = _baseline(projection=_projection(issue=issue))
    result = analyze_delivery_stockout(_payload(baseline=baseline))
    assert "issue-record:missing-1" in result.issue_refs
    assert "missing-1" not in result.issue_refs


def test_upstream_limitations_are_preserved_separately() -> None:
    baseline = _baseline(limitations=("upstream:limitation",))
    result = analyze_delivery_stockout(_payload(baseline=baseline))
    assert result.upstream_limitations == ("upstream:limitation",)
    assert result.limitation_codes == ()


def test_reference_deduplication_preserves_first_order() -> None:
    baseline = _baseline()
    baseline = baseline.model_copy(update={"evidence_refs": ("shared", "baseline-only"), "trace_refs": ("trace:shared",)})
    delivery = _delivery()
    delivery = delivery.model_copy(update={"evidence_refs": ("shared", "delivery-only"), "trace_refs": ("trace:shared", "trace:delivery")})
    result = analyze_delivery_stockout(_payload(baseline=baseline, delivery=delivery))
    assert result.evidence_refs == ("shared", "baseline-only", "delivery-only")
    assert result.trace_refs[0] == "trace:shared"
    assert len(result.trace_refs) == len(set(result.trace_refs))


def test_models_are_frozen_and_forbid_extra_fields() -> None:
    delivery = _delivery()
    with pytest.raises(ValidationError):
        delivery.expected_delivery_date = EVALUATION_DATE  # type: ignore[misc]
    with pytest.raises(ValidationError):
        PurchaseSpecificDeliveryTimingEvidence(
            **delivery.model_dump(),
            lead_time=10,
        )


def test_ent_result_does_not_expose_assessment_or_decision_fields() -> None:
    result = analyze_delivery_stockout(_payload())
    forbidden = {"outcome", "assessment_status", "recommendation", "decision", "effect", "severity"}
    assert forbidden.isdisjoint(result.model_fields)
    assert "lead_time" not in DeliveryStockoutAnalysisInput.model_fields
