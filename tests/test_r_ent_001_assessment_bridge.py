from datetime import date, timedelta
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation, Rule
from eios.delivery import (
    BaselineStockoutQualification,
    DeliveryStockoutAnalysisInput,
    PurchaseSpecificDeliveryTimingEvidence,
    analyze_delivery_stockout,
)
from eios.rules.delivery import (
    BASELINE_EVIDENCE_SOURCE_TYPE,
    DELIVERY_EVIDENCE_SOURCE_TYPE,
    evaluate_r_ent_001,
)
from eios.stock.models import (
    ConfiguredParameterValue,
    ProjectedDateMetric,
    ProjectedDecimalMetric,
    ProjectionHorizon,
    StockProjectionResult,
    StockResultIdentity,
)


EVALUATION_DATE = date(2026, 9, 11)
DECISION_ID = "DEC-ENT-BRIDGE-001"
ARTICLE_ID = "ART-001"
SUPPLIER_ID = "SUP-001"
PURCHASE_REF = "purchase-proposal:001"
RULES_VERSION = "rules-v1"
PARAMETERS_VERSION = "params-v1"
SNAPSHOT_ID = "snapshot-v1"
PURCHASE_SCENARIO = "SCN-PURCHASE"
BASELINE_SCENARIO = "SCN-BASE"


def _context(
    *,
    decision_id: str = DECISION_ID,
    rules_version: str = RULES_VERSION,
    parameters_version: str = PARAMETERS_VERSION,
    data_snapshot_id: str = SNAPSHOT_ID,
) -> DecisionContext:
    return DecisionContext(
        decision_id=decision_id,
        scenario_id=PURCHASE_SCENARIO,
        rules_version=rules_version,
        parameters_version=parameters_version,
        data_snapshot_id=data_snapshot_id,
    )


def _purchase(*, decision_id: str = DECISION_ID) -> PurchaseOperation:
    return PurchaseOperation(
        decision_id=decision_id,
        scenario_id=PURCHASE_SCENARIO,
        article_id=ARTICLE_ID,
        supplier_id=SUPPLIER_ID,
        quantity=Decimal("10"),
        unit_price=Decimal("5.00"),
        currency="EUR",
        operation_date=EVALUATION_DATE,
    )


def _rule(*, rule_id: str = "R-ENT-001", version: str = RULES_VERSION, requires_evidence: bool = True) -> Rule:
    return Rule(rule_id=rule_id, version=version, requires_evidence=requires_evidence)


def _horizon(*, parameters_version: str = PARAMETERS_VERSION) -> ProjectionHorizon:
    parameter = ConfiguredParameterValue(
        parameter_id="PYE-001",
        company_id="COMP-1",
        value=30,
        unit="day",
        state="KNOWN",
        parameters_version=parameters_version,
        applicable_reference_date=EVALUATION_DATE,
        configuration_ref="cfg:pye-001",
        source_ref="source:pye-001",
    )
    return ProjectionHorizon(
        parameter=parameter,
        horizon_days=30,
        horizon_end=EVALUATION_DATE + timedelta(days=30),
        state="KNOWN",
        trace_refs=("trace:horizon",),
    )


def _projection(
    *,
    depletion_state: str = "KNOWN",
    depletion_date: date | None = EVALUATION_DATE + timedelta(days=10),
    rules_version: str = RULES_VERSION,
    parameters_version: str = PARAMETERS_VERSION,
    data_snapshot_id: str = SNAPSHOT_ID,
) -> StockProjectionResult:
    identity = StockResultIdentity(
        decision_id=DECISION_ID,
        scenario_id=BASELINE_SCENARIO,
        rules_version=rules_version,
        parameters_version=parameters_version,
        data_snapshot_id=data_snapshot_id,
        company_id="COMP-1",
        operational_scope_id="OPS-1",
        article_id=ARTICLE_ID,
        evaluation_date=EVALUATION_DATE,
        base_unit="unit",
        methodology_version="0.1",
    )
    if depletion_state == "KNOWN":
        depletion = ProjectedDateMetric(
            value=depletion_date,
            state="KNOWN",
            trace_refs=("trace:depletion",),
        )
    else:
        depletion = ProjectedDateMetric(
            state=depletion_state,
            trace_refs=("trace:depletion",),
        )
    result_state = "KNOWN" if depletion_state in {"KNOWN", "NOT_APPLICABLE"} else depletion_state
    return StockProjectionResult(
        identity=identity,
        horizon=_horizon(parameters_version=parameters_version),
        minimum_projected_stock=ProjectedDecimalMetric(
            value=Decimal("1"),
            state="KNOWN",
            trace_refs=("trace:minimum",),
        ),
        depletion_date=depletion,
        state=result_state,
        trace_refs=("trace:projection",),
    )


def _baseline(*, projection: StockProjectionResult | None = None, state: str = "KNOWN") -> BaselineStockoutQualification:
    projection = projection or _projection()
    kwargs = dict(
        decision_id=DECISION_ID,
        article_id=ARTICLE_ID,
        evaluation_date=EVALUATION_DATE,
        evaluated_purchase_ref=PURCHASE_REF,
        baseline_projection_ref="stock-projection:baseline",
        projection=projection,
        state=state,
        evidence_refs=("evidence:baseline",),
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
    elif state == "NOT_DETERMINABLE":
        kwargs.update(unresolved_refs=("unresolved:baseline",))
    return BaselineStockoutQualification(**kwargs)


def _delivery(
    *,
    state: str = "KNOWN",
    expected_delivery_date: date | None = EVALUATION_DATE + timedelta(days=12),
) -> PurchaseSpecificDeliveryTimingEvidence:
    kwargs = dict(
        decision_id=DECISION_ID,
        article_id=ARTICLE_ID,
        supplier_id=SUPPLIER_ID,
        evaluation_date=EVALUATION_DATE,
        evaluated_purchase_ref=PURCHASE_REF,
        state=state,
        expected_delivery_date=expected_delivery_date,
        source_ref="source:delivery",
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
    elif state == "NOT_DETERMINABLE":
        kwargs.update(expected_delivery_date=None)
    elif state == "NOT_EVIDENCED":
        kwargs.update(expected_delivery_date=expected_delivery_date)
    return PurchaseSpecificDeliveryTimingEvidence(**kwargs)


def _analysis_pair(
    *,
    baseline: BaselineStockoutQualification | None = None,
    delivery: PurchaseSpecificDeliveryTimingEvidence | None = None,
):
    analysis_input = DeliveryStockoutAnalysisInput(
        decision_id=DECISION_ID,
        article_id=ARTICLE_ID,
        evaluation_date=EVALUATION_DATE,
        evaluated_purchase_ref=PURCHASE_REF,
        baseline=baseline or _baseline(),
        delivery=delivery or _delivery(),
    )
    return analysis_input, analyze_delivery_stockout(analysis_input)


def _baseline_evidence(*, state: str = "DEMONSTRATED", demonstration_ref: str | None = "trace:baseline") -> Evidence:
    return Evidence(
        evidence_id="EV-ENT-BASELINE",
        source_type=BASELINE_EVIDENCE_SOURCE_TYPE,
        source_ref="eios:ent:baseline:001",
        captured_at=EVALUATION_DATE,
        state=state,
        demonstration_ref=demonstration_ref if state == "DEMONSTRATED" else None,
    )


def _delivery_evidence(*, state: str = "DEMONSTRATED", demonstration_ref: str | None = "evidence:delivery") -> Evidence:
    return Evidence(
        evidence_id="EV-ENT-DELIVERY",
        source_type=DELIVERY_EVIDENCE_SOURCE_TYPE,
        source_ref="eios:ent:delivery:001",
        captured_at=EVALUATION_DATE,
        state=state,
        demonstration_ref=demonstration_ref if state == "DEMONSTRATED" else None,
    )


def _evaluate(
    analysis_input,
    analysis,
    *,
    purchase: PurchaseOperation | None = None,
    context: DecisionContext | None = None,
    rule: Rule | None = None,
    baseline_evidence: Evidence | None = None,
    delivery_evidence: Evidence | None = None,
):
    return evaluate_r_ent_001(
        purchase or _purchase(),
        context or _context(),
        rule or _rule(),
        analysis_input,
        analysis,
        baseline_evidence or _baseline_evidence(),
        delivery_evidence or _delivery_evidence(),
    )


def test_late_delivery_maps_to_evaluable_true() -> None:
    analysis_input, analysis = _analysis_pair()
    assessment = _evaluate(analysis_input, analysis)
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "TRUE"
    assert assessment.rule_id == "R-ENT-001"
    assert assessment.evidence_ids == ["EV-ENT-BASELINE", "EV-ENT-DELIVERY"]


def test_delivery_before_depletion_maps_to_false() -> None:
    analysis_input, analysis = _analysis_pair(
        delivery=_delivery(expected_delivery_date=EVALUATION_DATE + timedelta(days=5))
    )
    assessment = _evaluate(analysis_input, analysis)
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"
    assert "no posterior" in assessment.reason


def test_same_day_maps_to_false_and_preserves_intraday_limitation_in_reason() -> None:
    analysis_input, analysis = _analysis_pair(
        delivery=_delivery(expected_delivery_date=EVALUATION_DATE + timedelta(days=10))
    )
    assert "SAME_DAY_ORDER_NOT_DEMONSTRATED" in analysis.limitation_codes
    assessment = _evaluate(analysis_input, analysis)
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"
    assert "intradía" in assessment.reason


def test_no_depletion_within_horizon_maps_to_false_without_extrapolation() -> None:
    baseline = _baseline(projection=_projection(depletion_state="NOT_APPLICABLE", depletion_date=None))
    analysis_input, analysis = _analysis_pair(baseline=baseline)
    assert analysis.state == "NOT_LATE_WITHIN_EVIDENCED_HORIZON"
    assessment = _evaluate(analysis_input, analysis)
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"
    assert "horizonte STK evidenciado" in assessment.reason


def test_not_evidenced_ent_maps_to_not_evaluable() -> None:
    analysis_input, analysis = _analysis_pair(delivery=_delivery(state="NOT_EVIDENCED"))
    assert analysis.state == "NOT_EVIDENCED"
    assessment = _evaluate(
        analysis_input,
        analysis,
        delivery_evidence=_delivery_evidence(demonstration_ref="trace:delivery"),
    )
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_conflicting_ent_maps_to_not_evaluable() -> None:
    analysis_input, analysis = _analysis_pair(delivery=_delivery(state="CONFLICTING_DATA"))
    assert analysis.state == "CONFLICTING_DATA"
    delivery_evidence = _delivery_evidence(demonstration_ref="issue:delivery-conflict")
    assessment = _evaluate(analysis_input, analysis, delivery_evidence=delivery_evidence)
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None
    assert "contradictoria" in assessment.reason


def test_not_determinable_ent_maps_to_not_evaluable() -> None:
    analysis_input, analysis = _analysis_pair(baseline=_baseline(state="NOT_DETERMINABLE"))
    assert analysis.state == "NOT_DETERMINABLE"
    baseline_evidence = _baseline_evidence(demonstration_ref="unresolved:baseline")
    assessment = _evaluate(analysis_input, analysis, baseline_evidence=baseline_evidence)
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_conclusive_ent_with_baseline_gap_is_not_evaluable() -> None:
    analysis_input, analysis = _analysis_pair()
    assessment = _evaluate(
        analysis_input,
        analysis,
        baseline_evidence=_baseline_evidence(state="GAP", demonstration_ref=None),
    )
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_conclusive_ent_with_delivery_gap_is_not_evaluable() -> None:
    analysis_input, analysis = _analysis_pair()
    assessment = _evaluate(
        analysis_input,
        analysis,
        delivery_evidence=_delivery_evidence(state="GAP", demonstration_ref=None),
    )
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_wrong_baseline_source_type_is_rejected() -> None:
    analysis_input, analysis = _analysis_pair()
    wrong = _baseline_evidence().model_copy(update={"source_type": "OtherEvidence"})
    with pytest.raises(ValueError, match="baseline_evidence.source_type"):
        _evaluate(analysis_input, analysis, baseline_evidence=wrong)


def test_wrong_delivery_source_type_is_rejected() -> None:
    analysis_input, analysis = _analysis_pair()
    wrong = _delivery_evidence().model_copy(update={"source_type": "OtherEvidence"})
    with pytest.raises(ValueError, match="delivery_evidence.source_type"):
        _evaluate(analysis_input, analysis, delivery_evidence=wrong)


def test_unbound_baseline_demonstration_ref_is_rejected() -> None:
    analysis_input, analysis = _analysis_pair()
    with pytest.raises(ValueError, match="provenance baseline"):
        _evaluate(
            analysis_input,
            analysis,
            baseline_evidence=_baseline_evidence(demonstration_ref="unrelated:ref"),
        )


def test_unbound_delivery_demonstration_ref_is_rejected() -> None:
    analysis_input, analysis = _analysis_pair()
    with pytest.raises(ValueError, match="provenance delivery"):
        _evaluate(
            analysis_input,
            analysis,
            delivery_evidence=_delivery_evidence(demonstration_ref="unrelated:ref"),
        )


def test_wrong_rule_id_is_rejected() -> None:
    analysis_input, analysis = _analysis_pair()
    with pytest.raises(ValueError, match="solo evalúa R-ENT-001"):
        _evaluate(analysis_input, analysis, rule=_rule(rule_id="R-OTHER-001"))


def test_rule_version_mismatch_is_rejected() -> None:
    analysis_input, analysis = _analysis_pair()
    with pytest.raises(ValueError, match="Rule.version"):
        _evaluate(analysis_input, analysis, rule=_rule(version="rules-other"))


def test_rule_cannot_disable_required_evidence() -> None:
    analysis_input, analysis = _analysis_pair()
    with pytest.raises(ValueError, match="requiere evidencia"):
        _evaluate(analysis_input, analysis, rule=_rule(requires_evidence=False))


def test_purchase_and_context_identity_mismatch_is_rejected() -> None:
    analysis_input, analysis = _analysis_pair()
    with pytest.raises(ValueError, match="decision_id distintos"):
        _evaluate(analysis_input, analysis, purchase=_purchase(decision_id="OTHER-DEC"))


def test_stock_rules_version_mismatch_is_rejected() -> None:
    projection = _projection(rules_version="rules-other")
    analysis_input, analysis = _analysis_pair(baseline=_baseline(projection=projection))
    with pytest.raises(ValueError, match="otra rules_version"):
        _evaluate(analysis_input, analysis)


def test_stock_parameters_version_mismatch_is_rejected() -> None:
    projection = _projection(parameters_version="params-other")
    analysis_input, analysis = _analysis_pair(baseline=_baseline(projection=projection))
    with pytest.raises(ValueError, match="otra parameters_version"):
        _evaluate(analysis_input, analysis)


def test_stock_snapshot_mismatch_is_rejected() -> None:
    projection = _projection(data_snapshot_id="snapshot-other")
    analysis_input, analysis = _analysis_pair(baseline=_baseline(projection=projection))
    with pytest.raises(ValueError, match="otro data_snapshot_id"):
        _evaluate(analysis_input, analysis)


def test_baseline_scenario_may_differ_from_purchase_scenario() -> None:
    analysis_input, analysis = _analysis_pair()
    assert analysis_input.baseline.projection.identity.scenario_id == BASELINE_SCENARIO
    assert _purchase().scenario_id == PURCHASE_SCENARIO
    assessment = _evaluate(analysis_input, analysis)
    assert assessment.status == "EVALUABLE"


def test_expected_delivery_copy_mismatch_is_rejected() -> None:
    analysis_input, analysis = _analysis_pair()
    inconsistent = analysis.model_copy(
        update={"expected_delivery_date": EVALUATION_DATE + timedelta(days=13)}
    )
    with pytest.raises(ValueError, match="expected_delivery_date incompatibles"):
        _evaluate(analysis_input, inconsistent)


def test_depletion_copy_mismatch_is_rejected() -> None:
    analysis_input, analysis = _analysis_pair()
    inconsistent = analysis.model_copy(
        update={"depletion_date": EVALUATION_DATE + timedelta(days=9)}
    )
    with pytest.raises(ValueError, match="depletion_date incompatibles"):
        _evaluate(analysis_input, inconsistent)


def test_horizon_copy_mismatch_is_rejected() -> None:
    baseline = _baseline(projection=_projection(depletion_state="NOT_APPLICABLE", depletion_date=None))
    analysis_input, analysis = _analysis_pair(baseline=baseline)
    inconsistent = analysis.model_copy(
        update={"horizon_end": EVALUATION_DATE + timedelta(days=29)}
    )
    with pytest.raises(ValueError, match="horizon_end incompatibles"):
        _evaluate(analysis_input, inconsistent)


def test_internal_baseline_article_mismatch_is_rejected() -> None:
    analysis_input, _ = _analysis_pair()
    bad_baseline = analysis_input.baseline.model_copy(update={"article_id": "OTHER-ARTICLE"})
    bad_input = analysis_input.model_copy(update={"baseline": bad_baseline})
    analysis = analyze_delivery_stockout(bad_input)
    with pytest.raises(ValueError, match="Baseline pertenece a otro artículo"):
        _evaluate(bad_input, analysis)


def test_internal_delivery_purchase_ref_mismatch_is_rejected() -> None:
    analysis_input, _ = _analysis_pair()
    bad_delivery = analysis_input.delivery.model_copy(update={"evaluated_purchase_ref": "purchase:other"})
    bad_input = analysis_input.model_copy(update={"delivery": bad_delivery})
    analysis = analyze_delivery_stockout(bad_input)
    with pytest.raises(ValueError, match="Delivery evidence usa otro evaluated_purchase_ref"):
        _evaluate(bad_input, analysis)


def test_fabricated_late_result_with_not_evidenced_delivery_is_rejected() -> None:
    analysis_input, actual = _analysis_pair(delivery=_delivery(state="NOT_EVIDENCED"))
    fabricated = actual.model_copy(update={"state": "LATE_DELIVERY_DEMONSTRATED"})
    with pytest.raises(ValueError, match="requiere delivery KNOWN"):
        _evaluate(analysis_input, fabricated)


def test_fabricated_not_late_result_with_indeterminate_baseline_is_rejected() -> None:
    analysis_input, actual = _analysis_pair(baseline=_baseline(state="NOT_DETERMINABLE"))
    fabricated = actual.model_copy(update={"state": "NOT_LATE_DEMONSTRATED"})
    with pytest.raises(ValueError, match="requiere baseline KNOWN"):
        _evaluate(analysis_input, fabricated)


def test_fabricated_within_horizon_result_requires_not_applicable_depletion() -> None:
    analysis_input, actual = _analysis_pair()
    fabricated = actual.model_copy(update={"state": "NOT_LATE_WITHIN_EVIDENCED_HORIZON"})
    with pytest.raises(ValueError, match="requires depletion NOT_APPLICABLE|requiere depletion NOT_APPLICABLE"):
        _evaluate(analysis_input, fabricated)


def test_assessment_contract_does_not_gain_decisional_fields() -> None:
    analysis_input, analysis = _analysis_pair()
    assessment = _evaluate(analysis_input, analysis)
    forbidden = {"effect", "severity", "recommendation", "decision", "priority", "crc_result"}
    assert forbidden.isdisjoint(type(assessment).model_fields)


def test_bridge_does_not_invoke_ent_analyzer(monkeypatch) -> None:
    analysis_input, analysis = _analysis_pair()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Rules bridge no debe recalcular ENT")

    monkeypatch.setattr("eios.delivery.engine.analyze_delivery_stockout", fail_if_called)
    assessment = _evaluate(analysis_input, analysis)
    assert assessment.status == "EVALUABLE"
