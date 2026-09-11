from datetime import date, timedelta
from decimal import Decimal

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.capability_adapters import adapt_c0
from eios.core.crc_mvp import CRCInput, RuleMetadata, resolve_crc
from eios.core.models import DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.orchestration import O1ExecutionStatus
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
DECISION_ID = "DEC-ENT-VERTICAL-001"
ARTICLE_ID = "ART-001"
SUPPLIER_ID = "SUP-001"
PURCHASE_REF = "purchase-proposal:001"
RULES_VERSION = "rules-v1"
PARAMETERS_VERSION = "params-v1"
SNAPSHOT_ID = "snapshot-v1"


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id=DECISION_ID,
        scenario_id="SCN-PURCHASE",
        rules_version=RULES_VERSION,
        parameters_version=PARAMETERS_VERSION,
        data_snapshot_id=SNAPSHOT_ID,
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id=DECISION_ID,
        scenario_id="SCN-PURCHASE",
        article_id=ARTICLE_ID,
        supplier_id=SUPPLIER_ID,
        quantity=Decimal("10"),
        unit_price=Decimal("5.00"),
        currency="EUR",
        operation_date=EVALUATION_DATE,
    )


def _rule() -> Rule:
    return Rule(
        rule_id="R-ENT-001",
        version=RULES_VERSION,
        requires_evidence=True,
    )


def _projection() -> StockProjectionResult:
    parameter = ConfiguredParameterValue(
        parameter_id="PYE-001",
        company_id="COMP-1",
        value=30,
        unit="day",
        state="KNOWN",
        parameters_version=PARAMETERS_VERSION,
        applicable_reference_date=EVALUATION_DATE,
        configuration_ref="cfg:pye-001",
        source_ref="source:pye-001",
    )
    horizon = ProjectionHorizon(
        parameter=parameter,
        horizon_days=30,
        horizon_end=EVALUATION_DATE + timedelta(days=30),
        state="KNOWN",
        trace_refs=("trace:horizon",),
    )
    identity = StockResultIdentity(
        decision_id=DECISION_ID,
        scenario_id="SCN-BASE",
        rules_version=RULES_VERSION,
        parameters_version=PARAMETERS_VERSION,
        data_snapshot_id=SNAPSHOT_ID,
        company_id="COMP-1",
        operational_scope_id="OPS-1",
        article_id=ARTICLE_ID,
        evaluation_date=EVALUATION_DATE,
        base_unit="unit",
        methodology_version="0.1",
    )
    return StockProjectionResult(
        identity=identity,
        horizon=horizon,
        minimum_projected_stock=ProjectedDecimalMetric(
            value=Decimal("1"),
            state="KNOWN",
            trace_refs=("trace:minimum",),
        ),
        depletion_date=ProjectedDateMetric(
            value=EVALUATION_DATE + timedelta(days=10),
            state="KNOWN",
            trace_refs=("trace:depletion",),
        ),
        state="KNOWN",
        trace_refs=("trace:projection",),
    )


def _analysis_input(
    *,
    delivery_state: str = "KNOWN",
    expected_delivery_date: date | None = EVALUATION_DATE + timedelta(days=12),
) -> DeliveryStockoutAnalysisInput:
    baseline = BaselineStockoutQualification(
        decision_id=DECISION_ID,
        article_id=ARTICLE_ID,
        evaluation_date=EVALUATION_DATE,
        evaluated_purchase_ref=PURCHASE_REF,
        baseline_projection_ref="stock-projection:baseline",
        projection=_projection(),
        state="KNOWN",
        baseline_relation_ref="baseline:relation",
        projection_provenance_ref="baseline:provenance",
        purchase_exclusion_ref="baseline:purchase-excluded",
        evidence_refs=("evidence:baseline",),
        trace_refs=("trace:baseline",),
    )
    delivery_kwargs = dict(
        decision_id=DECISION_ID,
        article_id=ARTICLE_ID,
        supplier_id=SUPPLIER_ID,
        evaluation_date=EVALUATION_DATE,
        evaluated_purchase_ref=PURCHASE_REF,
        state=delivery_state,
        expected_delivery_date=expected_delivery_date,
        source_ref="source:delivery",
        trace_refs=("trace:delivery",),
    )
    if delivery_state == "KNOWN":
        delivery_kwargs.update(
            delivery_semantic_ref="semantic:expected-delivery-date",
            purchase_applicability_ref="applicability:purchase-001",
            evidence_refs=("evidence:delivery",),
            captured_at=EVALUATION_DATE,
        )
    delivery = PurchaseSpecificDeliveryTimingEvidence(**delivery_kwargs)
    return DeliveryStockoutAnalysisInput(
        decision_id=DECISION_ID,
        article_id=ARTICLE_ID,
        evaluation_date=EVALUATION_DATE,
        evaluated_purchase_ref=PURCHASE_REF,
        baseline=baseline,
        delivery=delivery,
    )


def _c0_evidence() -> tuple[Evidence, Evidence]:
    return (
        Evidence(
            evidence_id="EV-ENT-BASELINE",
            source_type=BASELINE_EVIDENCE_SOURCE_TYPE,
            source_ref="eios:ent:baseline:001",
            captured_at=EVALUATION_DATE,
            state="DEMONSTRATED",
            demonstration_ref="trace:baseline",
        ),
        Evidence(
            evidence_id="EV-ENT-DELIVERY",
            source_type=DELIVERY_EVIDENCE_SOURCE_TYPE,
            source_ref="eios:ent:delivery:001",
            captured_at=EVALUATION_DATE,
            state="DEMONSTRATED",
            demonstration_ref="trace:delivery",
        ),
    )


def _evaluate_chain(
    *,
    delivery_state: str = "KNOWN",
    expected_delivery_date: date | None = EVALUATION_DATE + timedelta(days=12),
):
    purchase = _purchase()
    context = _context()
    rule = _rule()
    analysis_input = _analysis_input(
        delivery_state=delivery_state,
        expected_delivery_date=expected_delivery_date,
    )
    analysis = analyze_delivery_stockout(analysis_input)
    baseline_evidence, delivery_evidence = _c0_evidence()
    assessment = evaluate_r_ent_001(
        purchase,
        context,
        rule,
        analysis_input,
        analysis,
        baseline_evidence,
        delivery_evidence,
    )
    trace = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    capability = adapt_c0((assessment,), (trace,))
    return (
        purchase,
        context,
        rule,
        analysis_input,
        analysis,
        assessment,
        trace,
        capability,
    )


def _metadata(*, version: str = RULES_VERSION) -> dict[str, RuleMetadata]:
    return {
        "R-ENT-001": RuleMetadata(
            rule_id="R-ENT-001",
            version=version,
            effect="R2",
            severity="ALTA",
        )
    }


def test_late_ent_composes_to_trace_adapter_and_isolated_crc_negotiation() -> None:
    _, context, _, _, _, assessment, trace, capability = _evaluate_chain()

    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "TRUE"
    assert trace.rule_id == "R-ENT-001"
    assert trace.assessment_status == "EVALUABLE"
    assert trace.assessment_outcome == "TRUE"
    assert trace.evidence_ids == tuple(assessment.evidence_ids)
    assert trace.decision_id == context.decision_id
    assert trace.scenario_id == context.scenario_id
    assert trace.rules_version == context.rules_version
    assert trace.parameters_version == context.parameters_version
    assert trace.data_snapshot_id == context.data_snapshot_id

    assert capability.capability == "C0"
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True
    assert capability.trace_references == (trace.trace_id,)

    crc = resolve_crc(
        CRCInput(
            assessments=[assessment],
            decision_context=context,
            base_result="COMPRAR",
        ),
        _metadata(),
    )
    assert crc.consolidated_result == "NEGOCIAR"
    assert crc.traceability.assessment_rule_ids == ("R-ENT-001",)


def test_false_ent_composes_and_crc_preserves_explicit_base_result() -> None:
    _, context, _, _, _, assessment, trace, capability = _evaluate_chain(
        expected_delivery_date=EVALUATION_DATE + timedelta(days=5)
    )

    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"
    assert trace.assessment_outcome == "FALSE"
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True

    crc = resolve_crc(
        CRCInput(
            assessments=[assessment],
            decision_context=context,
            base_result="COMPRAR",
        ),
        _metadata(),
    )
    assert crc.consolidated_result == "COMPRAR"


def test_not_evaluable_ent_composes_without_becoming_false() -> None:
    _, context, _, _, _, assessment, trace, capability = _evaluate_chain(
        delivery_state="NOT_EVIDENCED",
    )

    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None
    assert trace.assessment_status == "NOT_EVALUABLE"
    assert trace.assessment_outcome is None
    assert capability.status == O1ExecutionStatus.NOT_EVALUABLE
    assert capability.result_available is False
    assert capability.unresolved_items == ("C0_NOT_EVALUABLE",)

    crc = resolve_crc(
        CRCInput(
            assessments=[assessment],
            decision_context=context,
            base_result="COMPRAR",
        ),
        _metadata(),
    )
    assert crc.consolidated_result == "INFORMACIÓN INSUFICIENTE"


def test_trace_id_is_reproducible_for_same_material() -> None:
    purchase, context, rule, _, _, assessment, trace, _ = _evaluate_chain()
    repeated = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    assert repeated.trace_id == trace.trace_id
    assert repeated.input_fingerprint == trace.input_fingerprint


def test_crc_rejects_incompatible_runtime_rule_metadata_version() -> None:
    _, context, _, _, _, assessment, _, _ = _evaluate_chain()
    with pytest.raises(ValueError, match="rules_version"):
        resolve_crc(
            CRCInput(
                assessments=[assessment],
                decision_context=context,
                base_result="COMPRAR",
            ),
            _metadata(version="rules-other"),
        )


def test_rule_metadata_is_not_copied_into_assessment() -> None:
    _, _, _, _, _, assessment, _, _ = _evaluate_chain()
    forbidden = {"effect", "severity", "recommendation", "consolidated_result"}
    assert forbidden.isdisjoint(type(assessment).model_fields)


def test_composition_does_not_mutate_source_contracts() -> None:
    purchase = _purchase()
    context = _context()
    rule = _rule()
    analysis_input = _analysis_input()
    analysis = analyze_delivery_stockout(analysis_input)
    baseline_evidence, delivery_evidence = _c0_evidence()

    before = (
        purchase.model_dump(),
        context.model_dump(),
        rule.model_dump(),
        analysis_input.model_dump(),
        analysis.model_dump(),
        baseline_evidence.model_dump(),
        delivery_evidence.model_dump(),
    )

    assessment = evaluate_r_ent_001(
        purchase,
        context,
        rule,
        analysis_input,
        analysis,
        baseline_evidence,
        delivery_evidence,
    )
    trace = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    adapt_c0((assessment,), (trace,))
    resolve_crc(
        CRCInput(
            assessments=[assessment],
            decision_context=context,
            base_result="COMPRAR",
        ),
        _metadata(),
    )

    after = (
        purchase.model_dump(),
        context.model_dump(),
        rule.model_dump(),
        analysis_input.model_dump(),
        analysis.model_dump(),
        baseline_evidence.model_dump(),
        delivery_evidence.model_dump(),
    )
    assert after == before
