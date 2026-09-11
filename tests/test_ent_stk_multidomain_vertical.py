from datetime import date, timedelta
from decimal import Decimal

from eios.core.crc_mvp import RuleMetadata
from eios.core.models import DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.orchestration import O1ExecutionStatus
from eios.delivery import (
    BaselineStockoutQualification,
    DeliveryStockoutAnalysisInput,
    PurchaseSpecificDeliveryTimingEvidence,
    analyze_delivery_stockout,
)
from eios.rules import (
    BASELINE_EVIDENCE_SOURCE_TYPE,
    DELIVERY_EVIDENCE_SOURCE_TYPE,
    STOCK_EXCESS_EVIDENCE_SOURCE_TYPE,
    RuleAssessmentBinding,
    evaluate_r_ent_001,
    evaluate_r_stk_003,
    run_assessment_set_vertical,
)
from eios.stock.models import (
    ConfiguredParameterValue,
    ExcessResult,
    ProjectedDateMetric,
    ProjectedDecimalMetric,
    ProjectionHorizon,
    StockProjectionResult,
    StockReferenceValue,
    StockResultIdentity,
)


EVAL = date(2026, 9, 11)
DECISION = "D-ENT-STK"
SCENARIO = "S-PURCHASE"
ARTICLE = "ART-1"
SUPPLIER = "SUP-1"
RULES = "rules-v1"
PARAMS = "params-v1"
SNAPSHOT = "snapshot-v1"


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id=DECISION,
        scenario_id=SCENARIO,
        rules_version=RULES,
        parameters_version=PARAMS,
        data_snapshot_id=SNAPSHOT,
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id=DECISION,
        scenario_id=SCENARIO,
        article_id=ARTICLE,
        supplier_id=SUPPLIER,
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=EVAL,
    )


def _horizon() -> ProjectionHorizon:
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
    return ProjectionHorizon(
        parameter=parameter,
        horizon_days=30,
        horizon_end=EVAL + timedelta(days=30),
        state="KNOWN",
        trace_refs=("trace:horizon",),
    )


def _ent_projection() -> StockProjectionResult:
    identity = StockResultIdentity(
        decision_id=DECISION,
        scenario_id="S-BASE",
        rules_version=RULES,
        parameters_version=PARAMS,
        data_snapshot_id=SNAPSHOT,
        company_id="COMP-1",
        operational_scope_id="OPS-1",
        article_id=ARTICLE,
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="0.17",
    )
    return StockProjectionResult(
        identity=identity,
        horizon=_horizon(),
        minimum_projected_stock=ProjectedDecimalMetric(
            value=Decimal("1"), state="KNOWN", trace_refs=("trace:min",)
        ),
        depletion_date=ProjectedDateMetric(
            value=EVAL + timedelta(days=10),
            state="KNOWN",
            trace_refs=("trace:depletion",),
        ),
        state="KNOWN",
        trace_refs=("trace:baseline-projection",),
    )


def _ent_assessment(purchase: PurchaseOperation, context: DecisionContext):
    baseline = BaselineStockoutQualification(
        decision_id=DECISION,
        article_id=ARTICLE,
        evaluation_date=EVAL,
        evaluated_purchase_ref="purchase:1",
        baseline_projection_ref="stock:baseline",
        projection=_ent_projection(),
        state="KNOWN",
        baseline_relation_ref="baseline:relation",
        projection_provenance_ref="baseline:provenance",
        purchase_exclusion_ref="baseline:purchase-excluded",
        evidence_refs=("evidence:baseline",),
        trace_refs=("trace:baseline",),
    )
    delivery = PurchaseSpecificDeliveryTimingEvidence(
        decision_id=DECISION,
        article_id=ARTICLE,
        supplier_id=SUPPLIER,
        evaluation_date=EVAL,
        evaluated_purchase_ref="purchase:1",
        state="KNOWN",
        expected_delivery_date=EVAL + timedelta(days=12),
        delivery_semantic_ref="semantic:delivery-date",
        purchase_applicability_ref="applicability:purchase-1",
        source_ref="source:delivery",
        evidence_refs=("evidence:delivery",),
        trace_refs=("trace:delivery",),
        captured_at=EVAL,
    )
    payload = DeliveryStockoutAnalysisInput(
        decision_id=DECISION,
        article_id=ARTICLE,
        evaluation_date=EVAL,
        evaluated_purchase_ref="purchase:1",
        baseline=baseline,
        delivery=delivery,
    )
    analysis = analyze_delivery_stockout(payload)
    baseline_evidence = Evidence(
        evidence_id="EV-ENT-BASE",
        source_type=BASELINE_EVIDENCE_SOURCE_TYPE,
        source_ref="ent:baseline",
        captured_at=EVAL,
        state="DEMONSTRATED",
        demonstration_ref="trace:baseline",
    )
    delivery_evidence = Evidence(
        evidence_id="EV-ENT-DELIVERY",
        source_type=DELIVERY_EVIDENCE_SOURCE_TYPE,
        source_ref="ent:delivery",
        captured_at=EVAL,
        state="DEMONSTRATED",
        demonstration_ref="trace:delivery",
    )
    rule = Rule(rule_id="R-ENT-001", version=RULES, requires_evidence=True)
    assessment = evaluate_r_ent_001(
        purchase,
        context,
        rule,
        payload,
        analysis,
        baseline_evidence,
        delivery_evidence,
    )
    return rule, assessment


def _stk_assessment(purchase: PurchaseOperation, context: DecisionContext):
    identity = StockResultIdentity(
        decision_id=DECISION,
        scenario_id=SCENARIO,
        rules_version=RULES,
        parameters_version=PARAMS,
        data_snapshot_id=SNAPSHOT,
        company_id="COMP-1",
        operational_scope_id="OPS-1",
        article_id=ARTICLE,
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="0.17",
    )
    reference = StockReferenceValue(
        identity=identity,
        reference_kind="PROJECTED",
        reference_date=EVAL + timedelta(days=30),
        value=Decimal("120"),
        unit="unit",
        state="KNOWN",
        source_ref="stock:projected:purchase",
        trace_refs=("trace:stock-reference",),
    )
    excess = ExcessResult(
        identity=identity,
        stock_reference=reference,
        stock_maximum=Decimal("100"),
        excess_tolerance_quantity=Decimal("10"),
        excess_threshold=Decimal("110"),
        excess_quantity=Decimal("10"),
        state="EXCESS",
        trace_refs=("trace:excess",),
    )
    evidence = Evidence(
        evidence_id="EV-STK-EXCESS",
        source_type=STOCK_EXCESS_EVIDENCE_SOURCE_TYPE,
        source_ref="stock:m07",
        captured_at=EVAL,
        state="DEMONSTRATED",
        demonstration_ref="trace:excess",
    )
    rule = Rule(rule_id="R-STK-003", version=RULES, requires_evidence=True)
    assessment = evaluate_r_stk_003(purchase, context, rule, excess, evidence)
    return rule, assessment


def test_ent_and_stock_rules_run_together_through_crc_and_o1() -> None:
    context = _context()
    purchase = _purchase()
    ent_rule, ent_assessment = _ent_assessment(purchase, context)
    stk_rule, stk_assessment = _stk_assessment(purchase, context)

    assert ent_assessment.outcome == "TRUE"
    assert stk_assessment.outcome == "TRUE"

    result = run_assessment_set_vertical(
        purchase=purchase,
        context=context,
        bindings=(
            RuleAssessmentBinding(
                rule=ent_rule,
                assessment=ent_assessment,
                metadata=RuleMetadata(
                    rule_id="R-ENT-001", version=RULES, effect="R2", severity="ALTA"
                ),
            ),
            RuleAssessmentBinding(
                rule=stk_rule,
                assessment=stk_assessment,
                metadata=RuleMetadata(
                    rule_id="R-STK-003", version=RULES, effect="R2", severity="ALTA"
                ),
            ),
        ),
        base_result="COMPRAR",
    )

    assert tuple(item.rule_id for item in result.assessments) == (
        "R-ENT-001",
        "R-STK-003",
    )
    assert tuple(trace.rule_id for trace in result.traces) == (
        "R-ENT-001",
        "R-STK-003",
    )
    assert result.crc_result.consolidated_result == "NEGOCIAR"
    assert result.c0_capability.status == O1ExecutionStatus.COMPLETED
    assert result.support_package.execution_status == O1ExecutionStatus.COMPLETED
    assert result.support_package.trace_references == tuple(
        trace.trace_id for trace in result.traces
    )
