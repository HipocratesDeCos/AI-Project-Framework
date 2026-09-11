from datetime import date
from decimal import Decimal

from eios.core.crc_mvp import RuleMetadata
from eios.core.models import DecisionContext, Evidence, PurchaseOperation, Rule
from eios.rules import (
    R_STK_003,
    R_STK_004,
    STOCK_CONFIRMED_DEMAND_EVIDENCE_SOURCE_TYPE,
    STOCK_EXCESS_EVIDENCE_SOURCE_TYPE,
    RuleAssessmentBinding,
    evaluate_r_stk_003,
    evaluate_r_stk_004,
    run_assessment_set_vertical,
)
from eios.stock.models import (
    AllocationLedgerEntry,
    AllocationLedgerSnapshot,
    ConfirmedDemandAbsorptionResult,
    DemandAllocation,
    ExcessResult,
    StockReferenceValue,
    StockResultIdentity,
    StockScope,
)


EVAL = date(2026, 9, 11)
SCOPE = StockScope(company_id="COMP-1", operational_scope_id="OPS-1")
CONTEXT = DecisionContext(
    decision_id="D-STK-EXC",
    scenario_id="S-PURCHASE",
    rules_version="rules-v1",
    parameters_version="params-v1",
    data_snapshot_id="snapshot-v1",
)
PURCHASE = PurchaseOperation(
    decision_id="D-STK-EXC",
    scenario_id="S-PURCHASE",
    article_id="ART-1",
    supplier_id="SUP-1",
    quantity=Decimal("10"),
    unit_price=Decimal("5"),
    currency="EUR",
    operation_date=EVAL,
)


def _identity() -> StockResultIdentity:
    return StockResultIdentity(
        decision_id=CONTEXT.decision_id,
        scenario_id=CONTEXT.scenario_id,
        rules_version=CONTEXT.rules_version,
        parameters_version=CONTEXT.parameters_version,
        data_snapshot_id=CONTEXT.data_snapshot_id,
        company_id=SCOPE.company_id,
        operational_scope_id=SCOPE.operational_scope_id,
        article_id=PURCHASE.article_id,
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="0.17",
    )


def _excess() -> ExcessResult:
    identity = _identity()
    reference = StockReferenceValue(
        identity=identity,
        reference_kind="PROJECTED",
        reference_date=EVAL,
        value=Decimal("120"),
        unit="unit",
        state="KNOWN",
        source_ref="stock:projected",
        trace_refs=("trace:stock-reference",),
    )
    return ExcessResult(
        identity=identity,
        stock_reference=reference,
        stock_maximum=Decimal("100"),
        excess_tolerance_quantity=Decimal("10"),
        excess_threshold=Decimal("110"),
        excess_quantity=Decimal("10"),
        state="EXCESS",
        trace_refs=("trace:excess",),
    )


def _absorption(state="APLICABLE_Y_VALIDADA") -> ConfirmedDemandAbsorptionResult:
    excess = _excess()
    if state == "APLICABLE_Y_VALIDADA":
        allocation = DemandAllocation(
            allocation_entry_id="ALLOC-1",
            confirmed_demand_id="ORDER-1",
            quantity_to_apply=Decimal("10"),
            unit="unit",
            allocation_source_ref="allocation:m08:1",
            trace_refs=("trace:allocation",),
        )
        entry = AllocationLedgerEntry(
            allocation_entry_id="ALLOC-1",
            confirmed_demand_id="ORDER-1",
            scope=SCOPE,
            article_id=PURCHASE.article_id,
            allocated_quantity=Decimal("10"),
            unit="unit",
            decision_id=CONTEXT.decision_id,
            scenario_id=CONTEXT.scenario_id,
            excess_reference_date=EVAL,
            allocation_result_ref="allocation:m08:1",
            trace_refs=("trace:allocation",),
        )
        ledger = AllocationLedgerSnapshot(
            reference_date=EVAL,
            scope=SCOPE,
            article_id=PURCHASE.article_id,
            state="KNOWN",
            entries=(entry,),
            source_ref="ledger:m08",
            trace_refs=("trace:ledger",),
        )
        return ConfirmedDemandAbsorptionResult(
            identity=excess.identity,
            excess_result=excess,
            business_state=state,
            total_remaining_applicable=Decimal("20"),
            absorbed_excess=Decimal("10"),
            residual_excess=Decimal("0"),
            allocation_plan=(allocation,),
            resulting_ledger=ledger,
            trace_refs=("trace:m08",),
        )
    if state in {"NO_EXISTE", "NO_APLICABLE"}:
        return ConfirmedDemandAbsorptionResult(
            identity=excess.identity,
            excess_result=excess,
            business_state=state,
            total_remaining_applicable=Decimal("0"),
            absorbed_excess=Decimal("0"),
            residual_excess=Decimal("10"),
            trace_refs=("trace:m08",),
        )
    return ConfirmedDemandAbsorptionResult(
        identity=excess.identity,
        excess_result=excess,
        business_state="NO_VERIFICABLE",
        trace_refs=("trace:m08",),
    )


def _m07_evidence() -> Evidence:
    return Evidence(
        evidence_id="EV-M07",
        source_type=STOCK_EXCESS_EVIDENCE_SOURCE_TYPE,
        source_ref="stock:m07",
        captured_at=EVAL,
        state="DEMONSTRATED",
        demonstration_ref="trace:excess",
    )


def _m08_evidence(state="DEMONSTRATED") -> Evidence:
    return Evidence(
        evidence_id="EV-M08",
        source_type=STOCK_CONFIRMED_DEMAND_EVIDENCE_SOURCE_TYPE,
        source_ref="stock:m08",
        captured_at=EVAL,
        state=state,
        demonstration_ref="trace:m08" if state == "DEMONSTRATED" else None,
    )


def test_confirmed_demand_absorption_maps_to_true_exception() -> None:
    rule = Rule(rule_id=R_STK_004, version="rules-v1", requires_evidence=True)
    assessment = evaluate_r_stk_004(PURCHASE, CONTEXT, rule, _absorption(), _m08_evidence())
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "TRUE"


def test_no_order_or_non_applicable_order_maps_to_false() -> None:
    rule = Rule(rule_id=R_STK_004, version="rules-v1", requires_evidence=True)
    for state in ("NO_EXISTE", "NO_APLICABLE"):
        assessment = evaluate_r_stk_004(PURCHASE, CONTEXT, rule, _absorption(state), _m08_evidence())
        assert assessment.status == "EVALUABLE"
        assert assessment.outcome == "FALSE"


def test_non_verifiable_mitigation_never_becomes_false() -> None:
    rule = Rule(rule_id=R_STK_004, version="rules-v1", requires_evidence=True)
    assessment = evaluate_r_stk_004(
        PURCHASE, CONTEXT, rule, _absorption("NO_VERIFICABLE"), _m08_evidence()
    )
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_m07_excess_and_m08_exception_are_jointly_resolved_without_rewriting_excess() -> None:
    excess = _excess()
    absorption = _absorption()
    rule_003 = Rule(rule_id=R_STK_003, version="rules-v1", requires_evidence=True)
    rule_004 = Rule(rule_id=R_STK_004, version="rules-v1", requires_evidence=True)
    assessment_003 = evaluate_r_stk_003(PURCHASE, CONTEXT, rule_003, excess, _m07_evidence())
    assessment_004 = evaluate_r_stk_004(PURCHASE, CONTEXT, rule_004, absorption, _m08_evidence())

    assert assessment_003.outcome == "TRUE"
    assert assessment_004.outcome == "TRUE"
    assert excess.excess_quantity == Decimal("10")
    assert absorption.absorbed_excess == Decimal("10")

    result = run_assessment_set_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        bindings=(
            RuleAssessmentBinding(
                rule=rule_003,
                assessment=assessment_003,
                metadata=RuleMetadata(
                    rule_id=R_STK_003, version="rules-v1", effect="R2", severity="ALTA"
                ),
            ),
            RuleAssessmentBinding(
                rule=rule_004,
                assessment=assessment_004,
                metadata=RuleMetadata(
                    rule_id=R_STK_004, version="rules-v1", effect="R1", severity="ALTA"
                ),
            ),
        ),
        base_result="COMPRAR",
    )
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"
    assert any(item.startswith(f"{R_STK_003}:R2") for item in result.crc_result.conflicts)


def test_gap_m08_evidence_blocks_conclusive_exception() -> None:
    rule = Rule(rule_id=R_STK_004, version="rules-v1", requires_evidence=True)
    assessment = evaluate_r_stk_004(PURCHASE, CONTEXT, rule, _absorption(), _m08_evidence("GAP"))
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None
