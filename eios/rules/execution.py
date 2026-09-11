"""Unified execution service for implemented EIOS business-rule bridges.

The service evaluates only rule inputs explicitly supplied by the caller. It
never discovers dependencies, invents missing facts, or marks an omitted rule
as NOT_EVALUABLE. Produced Assessments are then consolidated through the
catalog-backed vertical runtime (Trace -> C0 adapter -> CRC -> O1).
"""
from __future__ import annotations

from dataclasses import dataclass

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.delivery.models import DeliveryStockoutAnalysisInput, DeliveryStockoutAnalysisResult
from eios.finance import FinanceBasicInput, FinanceBasicResult
from eios.parameters import ResolvedConfiguration
from eios.pricing import PriceIntelligenceInput, PriceIntelligenceResult
from eios.stock.models import ConfirmedDemandAbsorptionResult, ExcessResult

from .catalog import authorized_rule, implemented_rule_ids
from .delivery import R_ENT_001, evaluate_r_ent_001
from .finance import R_FIN_001, R_FIN_003, evaluate_r_fin_001, evaluate_r_fin_003
from .pricing import R_HIS_002, evaluate_r_his_002
from .runtime import ConsolidatedBaseResult, RuleSetVerticalResult, run_authorized_assessments_vertical
from .stock import R_STK_003, R_STK_004, evaluate_r_stk_003, evaluate_r_stk_004


@dataclass(frozen=True)
class DeliveryRuleInputs:
    analysis_input: DeliveryStockoutAnalysisInput
    analysis: DeliveryStockoutAnalysisResult
    baseline_evidence: Evidence
    delivery_evidence: Evidence


@dataclass(frozen=True)
class StockExcessRuleInputs:
    excess: ExcessResult
    stock_evidence: Evidence


@dataclass(frozen=True)
class StockAbsorptionRuleInputs:
    absorption: ConfirmedDemandAbsorptionResult
    confirmed_demand_evidence: Evidence


@dataclass(frozen=True)
class FinanceCapacityRuleInputs:
    finance_input: FinanceBasicInput
    finance_result: FinanceBasicResult
    finance_evidence: Evidence
    threshold_resolution: ResolvedConfiguration | None
    parameter_evidence: Evidence | None


@dataclass(frozen=True)
class FinanceSafetyMarginRuleInputs:
    finance_input: FinanceBasicInput
    finance_result: FinanceBasicResult
    finance_evidence: Evidence
    treasury_minimum_resolution: ResolvedConfiguration | None
    treasury_minimum_evidence: Evidence | None
    margin_resolution: ResolvedConfiguration | None
    margin_evidence: Evidence | None


@dataclass(frozen=True)
class HistorySufficiencyRuleInputs:
    pricing_input: PriceIntelligenceInput
    pricing_result: PriceIntelligenceResult
    pricing_evidence: Evidence
    company_id: str
    minimum_resolution: ResolvedConfiguration | None
    parameter_evidence: Evidence | None


def run_decision_rules(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    base_result: ConsolidatedBaseResult,
    delivery: DeliveryRuleInputs | None = None,
    stock_excess: StockExcessRuleInputs | None = None,
    stock_absorption: StockAbsorptionRuleInputs | None = None,
    finance_capacity: FinanceCapacityRuleInputs | None = None,
    finance_safety_margin: FinanceSafetyMarginRuleInputs | None = None,
    history_sufficiency: HistorySufficiencyRuleInputs | None = None,
) -> RuleSetVerticalResult:
    """Evaluate supplied implemented rules and consolidate them in one call.

    Omitted rule inputs are omitted from this execution; they are not silently
    converted to NOT_EVALUABLE. Each supplied bridge remains responsible for
    its own evidence and identity validation.
    """
    assessments_by_rule = {}

    if delivery is not None:
        rule = authorized_rule(R_ENT_001, context.rules_version)
        assessments_by_rule[R_ENT_001] = evaluate_r_ent_001(
            purchase,
            context,
            rule,
            delivery.analysis_input,
            delivery.analysis,
            delivery.baseline_evidence,
            delivery.delivery_evidence,
        )

    if stock_excess is not None:
        rule = authorized_rule(R_STK_003, context.rules_version)
        assessments_by_rule[R_STK_003] = evaluate_r_stk_003(
            purchase,
            context,
            rule,
            stock_excess.excess,
            stock_excess.stock_evidence,
        )

    if stock_absorption is not None:
        rule = authorized_rule(R_STK_004, context.rules_version)
        assessments_by_rule[R_STK_004] = evaluate_r_stk_004(
            purchase,
            context,
            rule,
            stock_absorption.absorption,
            stock_absorption.confirmed_demand_evidence,
        )

    if finance_capacity is not None:
        rule = authorized_rule(R_FIN_001, context.rules_version)
        assessments_by_rule[R_FIN_001] = evaluate_r_fin_001(
            purchase,
            context,
            rule,
            finance_capacity.finance_input,
            finance_capacity.finance_result,
            finance_capacity.finance_evidence,
            finance_capacity.threshold_resolution,
            finance_capacity.parameter_evidence,
        )

    if finance_safety_margin is not None:
        rule = authorized_rule(R_FIN_003, context.rules_version)
        assessments_by_rule[R_FIN_003] = evaluate_r_fin_003(
            purchase,
            context,
            rule,
            finance_safety_margin.finance_input,
            finance_safety_margin.finance_result,
            finance_safety_margin.finance_evidence,
            finance_safety_margin.treasury_minimum_resolution,
            finance_safety_margin.treasury_minimum_evidence,
            finance_safety_margin.margin_resolution,
            finance_safety_margin.margin_evidence,
        )

    if history_sufficiency is not None:
        rule = authorized_rule(R_HIS_002, context.rules_version)
        assessments_by_rule[R_HIS_002] = evaluate_r_his_002(
            purchase,
            context,
            rule,
            history_sufficiency.pricing_input,
            history_sufficiency.pricing_result,
            history_sufficiency.pricing_evidence,
            history_sufficiency.company_id,
            history_sufficiency.minimum_resolution,
            history_sufficiency.parameter_evidence,
        )

    ordered_assessments = tuple(
        assessments_by_rule[rule_id]
        for rule_id in implemented_rule_ids()
        if rule_id in assessments_by_rule
    )
    return run_authorized_assessments_vertical(
        purchase=purchase,
        context=context,
        assessments=ordered_assessments,
        base_result=base_result,
    )


__all__ = [
    "DeliveryRuleInputs",
    "FinanceCapacityRuleInputs",
    "FinanceSafetyMarginRuleInputs",
    "HistorySufficiencyRuleInputs",
    "StockAbsorptionRuleInputs",
    "StockExcessRuleInputs",
    "run_decision_rules",
]
