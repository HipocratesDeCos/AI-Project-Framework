from datetime import date, timedelta
from decimal import Decimal

import pytest

from eios.core.crc_mvp import RuleMetadata
from eios.core.models import DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.orchestration import O1ExecutionStatus
from eios.delivery import (
    BaselineStockoutQualification,
    DeliveryStockoutAnalysisInput,
    PurchaseSpecificDeliveryTimingEvidence,
)
from eios.rules import (
    BASELINE_EVIDENCE_SOURCE_TYPE,
    DELIVERY_EVIDENCE_SOURCE_TYPE,
    run_r_ent_001_vertical,
)
from eios.stock.models import (
    ConfiguredParameterValue,
    ProjectedDateMetric,
    ProjectedDecimalMetric,
    ProjectionHorizon,
    StockProjectionResult,
    StockResultIdentity,
)


EVAL = date(2026, 9, 11)
DECISION = "DEC-VERTICAL-ENT"
ARTICLE = "ART-1"
SUPPLIER = "SUP-1"
RULES = "rules-v1"
PARAMS = "params-v1"
SNAPSHOT = "snapshot-v1"
PURCHASE_REF = "purchase:proposal:1"


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id=DECISION,
        scenario_id="SCN-PURCHASE",
        rules_version=RULES,
        parameters_version=PARAMS,
        data_snapshot_id=SNAPSHOT,
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id=DECISION,
        scenario_id="SCN-PURCHASE",
        article_id=ARTICLE,
        supplier_id=SUPPLIER,
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=EVAL,
    )


def _rule() -> Rule:
    return Rule(rule_id="R-ENT-001", version=RULES, requires_evidence=True)


def _metadata(*, effect="R2", severity="ALTA", version=RULES) -> RuleMetadata:
    return RuleMetadata(
        rule_id="R-ENT-001",
        version=version,
        effect=effect,
        severity=severity,
    )


def _projection(*, depletion_state="KNOWN", depletion_offset=10) -> StockProjectionResult:
    parameter = ConfiguredParameterValue(
        parameter_id="PYE-001",
        company_id="COMP-1",
        value=30,
        unit="day",
        state="KNOWN",
        parameters_version=PARAMS,
        applicable_reference_date=EVAL,
        configuration_ref="cfg:pye-001",
        source_ref="src:pye-001",
    )
    horizon = ProjectionHorizon(
        parameter=parameter,
        horizon_days=30,
        horizon_end=EVAL + timedelta(days=30),
        state="KNOWN",
        trace_refs=("trace:horizon",),
    )
    identity = StockResultIdentity(
        decision_id=DECISION,
        scenario_id="SCN-BASE",
        rules_version=RULES,
        parameters_version=PARAMS,
        data_snapshot_id=SNAPSHOT,
        company_id="COMP-1",
        operational_scope_id="OPS-1",
        article_id=ARTICLE,
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="0.1",
    )
    depletion = ProjectedDateMetric(
        value=EVAL + timedelta(days=depletion_offset) if depletion_state == "KNOWN" else None,
        state=depletion_state,
        trace_refs=("trace:depletion",),
    )
    return StockProjectionResult(
        identity=identity,
        horizon=horizon,
        minimum_projected_stock=ProjectedDecimalMetric(
            value=Decimal("1"),
            state="KNOWN",
            trace_refs=("trace:minimum",),
        ),
        depletion_date=depletion,
        state="KNOWN" if depletion_state in {"KNOWN", "NOT_APPLICABLE"} else depletion_state,
        trace_refs=("trace:projection",),
    )


def _analysis_input(*, delivery_offset=12, delivery_state="KNOWN") -> DeliveryStockoutAnalysisInput:
    baseline = BaselineStockoutQualification(
        decision_id=DECISION,
        article_id=ARTICLE,
        evaluation_date=EVAL,
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
    kwargs = dict(
        decision_id=DECISION,
        article_id=ARTICLE,
        supplier_id=SUPPLIER,
        evaluation_date=EVAL,
        evaluated_purchase_ref=PURCHASE_REF,
        state=delivery_state,
        expected_delivery_date=EVAL + timedelta(days=delivery_offset),
        source_ref="source:delivery",
        trace_refs=("trace:delivery",),
    )
    if delivery_state == "KNOWN":
        kwargs.update(
            delivery_semantic_ref="semantic:delivery-date",
            purchase_applicability_ref="applicability:purchase-1",
            evidence_refs=("evidence:delivery",),
            captured_at=EVAL,
        )
    return DeliveryStockoutAnalysisInput(
        decision_id=DECISION,
        article_id=ARTICLE,
        evaluation_date=EVAL,
        evaluated_purchase_ref=PURCHASE_REF,
        baseline=baseline,
        delivery=PurchaseSpecificDeliveryTimingEvidence(**kwargs),
    )


def _evidence(*, delivery_demonstrated=True) -> tuple[Evidence, Evidence]:
    baseline = Evidence(
        evidence_id="EV-BASE",
        source_type=BASELINE_EVIDENCE_SOURCE_TYPE,
        source_ref="ent:baseline",
        captured_at=EVAL,
        state="DEMONSTRATED",
        demonstration_ref="trace:baseline",
    )
    delivery = Evidence(
        evidence_id="EV-DELIVERY",
        source_type=DELIVERY_EVIDENCE_SOURCE_TYPE,
        source_ref="ent:delivery",
        captured_at=EVAL,
        state="DEMONSTRATED" if delivery_demonstrated else "GAP",
        demonstration_ref="trace:delivery" if delivery_demonstrated else None,
    )
    return baseline, delivery


def _run(*, delivery_offset=12, delivery_state="KNOWN", base_result="COMPRAR", metadata=None):
    baseline_evidence, delivery_evidence = _evidence(
        delivery_demonstrated=delivery_state == "KNOWN"
    )
    return run_r_ent_001_vertical(
        purchase=_purchase(),
        context=_context(),
        rule=_rule(),
        analysis_input=_analysis_input(
            delivery_offset=delivery_offset,
            delivery_state=delivery_state,
        ),
        baseline_evidence=baseline_evidence,
        delivery_evidence=delivery_evidence,
        base_result=base_result,
        rule_metadata=metadata or _metadata(),
    )


def test_runtime_late_delivery_reaches_crc_and_o1_package() -> None:
    result = _run()

    assert result.analysis.state == "LATE_DELIVERY_DEMONSTRATED"
    assert result.assessment.status == "EVALUABLE"
    assert result.assessment.outcome == "TRUE"
    assert result.trace.rule_id == "R-ENT-001"
    assert result.c0_capability.status == O1ExecutionStatus.COMPLETED
    assert result.crc_result.consolidated_result == "NEGOCIAR"
    assert result.support_package.execution_status == O1ExecutionStatus.COMPLETED
    assert result.support_package.trace_references == (result.trace.trace_id,)


def test_runtime_false_rule_preserves_explicit_crc_base_result() -> None:
    result = _run(delivery_offset=5, base_result="COMPRAR CONDICIONADO")

    assert result.analysis.state == "NOT_LATE_DEMONSTRATED"
    assert result.assessment.outcome == "FALSE"
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"
    assert result.support_package.execution_status == O1ExecutionStatus.COMPLETED


def test_runtime_not_evaluable_propagates_to_crc_and_support_package() -> None:
    result = _run(delivery_state="NOT_EVIDENCED")

    assert result.assessment.status == "NOT_EVALUABLE"
    assert result.assessment.outcome is None
    assert result.c0_capability.status == O1ExecutionStatus.NOT_EVALUABLE
    assert result.crc_result.consolidated_result == "INFORMACIÓN INSUFICIENTE"
    assert result.support_package.execution_status == O1ExecutionStatus.PARTIALLY_COMPLETED
    assert result.support_package.unresolved_items == ("C0_NOT_EVALUABLE",)


def test_runtime_rejects_normative_metadata_not_authorized_for_r_ent_001() -> None:
    with pytest.raises(ValueError, match="R2 / ALTA"):
        _run(metadata=_metadata(effect="R1"))


def test_runtime_rejects_metadata_version_mismatch_before_crc() -> None:
    with pytest.raises(ValueError, match="RuleMetadata.version"):
        _run(metadata=_metadata(version="rules-other"))


def test_runtime_trace_is_reproducible_for_same_material() -> None:
    first = _run()
    second = _run()
    assert first.trace.trace_id == second.trace.trace_id
    assert first.trace.input_fingerprint == second.trace.input_fingerprint
    assert first.crc_result.consolidated_result == second.crc_result.consolidated_result
