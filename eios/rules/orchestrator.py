"""Domain-to-rules orchestration for implemented EIOS business rules.

This layer converts domain results into individual Assessments inside the same
purchase/context execution, then composes those freshly-produced results through
the internal same-execution runtime. It does not use the public provenance reuse
boundary because no detached Assessment crosses a boundary here.
"""
from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.delivery.models import DeliveryStockoutAnalysisInput, DeliveryStockoutAnalysisResult
from eios.finance import ProvenancedFinanceBasicExecution
from eios.parameters import ResolvedConfiguration
from eios.pricing import PriceIntelligenceAssessmentContext, PriceIntelligenceInput
from eios.profitability import ProvenancedProfitabilityExecution
from eios.stock.models import ConfirmedDemandAbsorptionResult, ExcessResult

from .catalog import authorized_rule, implemented_rule_ids
from .delivery import R_ENT_001, R_STK_001, evaluate_r_ent_001, evaluate_r_stk_001
from .finance import R_FIN_001, R_FIN_003, evaluate_r_fin_001, evaluate_r_fin_003
from .pricing import R_HIS_002, evaluate_r_his_002
from .profitability import (
    MGEParameterBundle,
    R_MGE_001,
    R_MGE_002,
    R_MGE_003,
    evaluate_r_mge_001,
    evaluate_r_mge_002,
    evaluate_r_mge_003,
)
from .runtime import (
    ConsolidatedBaseResult,
    RuleSetVerticalResult,
    run_authorized_assessments_vertical,
)
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
    finance_execution: ProvenancedFinanceBasicExecution
    finance_evidence: Evidence
    threshold_resolution: ResolvedConfiguration | None
    parameter_evidence: Evidence | None


@dataclass(frozen=True)
class FinanceSafetyMarginRuleInputs:
    finance_execution: ProvenancedFinanceBasicExecution
    finance_evidence: Evidence
    treasury_minimum_resolution: ResolvedConfiguration | None
    treasury_minimum_evidence: Evidence | None
    margin_resolution: ResolvedConfiguration | None
    margin_evidence: Evidence | None


@dataclass(frozen=True)
class HistorySufficiencyRuleInputs:
    pricing_input: PriceIntelligenceInput
    pricing_assessment_context: PriceIntelligenceAssessmentContext
    pricing_evidence: Evidence
    company_id: str
    minimum_resolution: ResolvedConfiguration | None
    parameter_evidence: Evidence | None


@dataclass(frozen=True)
class ProfitabilityRuleInputs:
    profitability_execution: ProvenancedProfitabilityExecution
    profitability_evidence: Evidence
    minimum_resolution: ResolvedConfiguration | None
    minimum_evidence: Evidence | None
    target_resolution: ResolvedConfiguration | None
    target_evidence: Evidence | None
    tolerance_resolution: ResolvedConfiguration | None
    tolerance_evidence: Evidence | None


class DecisionRuleExecutionResult(BaseModel):
    """Rules result plus explicit coverage of implemented rule bridges."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    executed_rule_ids: tuple[str, ...]
    omitted_rule_ids: tuple[str, ...]
    rules_engine_result: RuleSetVerticalResult

    @property
    def assessments(self):
        return self.rules_engine_result.assessments

    @property
    def traces(self):
        return self.rules_engine_result.traces

    @property
    def crc_result(self):
        return self.rules_engine_result.crc_result

    @property
    def c0_capability(self):
        return self.rules_engine_result.c0_capability

    @property
    def support_package(self):
        return self.rules_engine_result.support_package


def run_domain_rules(
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
    profitability: ProfitabilityRuleInputs | None = None,
) -> DecisionRuleExecutionResult:
    """Evaluate supplied domain bundles and compose them in the same execution."""
    assessments_by_rule = {}

    if delivery is not None:
        ent_rule = authorized_rule(R_ENT_001, context.rules_version)
        assessments_by_rule[R_ENT_001] = evaluate_r_ent_001(
            purchase,
            context,
            ent_rule,
            delivery.analysis_input,
            delivery.analysis,
            delivery.baseline_evidence,
            delivery.delivery_evidence,
        )
        stockout_rule = authorized_rule(R_STK_001, context.rules_version)
        assessments_by_rule[R_STK_001] = evaluate_r_stk_001(
            purchase,
            context,
            stockout_rule,
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
            finance_capacity.finance_execution,
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
            finance_safety_margin.finance_execution,
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
            history_sufficiency.pricing_assessment_context,
            history_sufficiency.pricing_evidence,
            history_sufficiency.company_id,
            history_sufficiency.minimum_resolution,
            history_sufficiency.parameter_evidence,
        )

    if profitability is not None:
        bundle = MGEParameterBundle(
            minimum_resolution=profitability.minimum_resolution,
            minimum_evidence=profitability.minimum_evidence,
            target_resolution=profitability.target_resolution,
            target_evidence=profitability.target_evidence,
            tolerance_resolution=profitability.tolerance_resolution,
            tolerance_evidence=profitability.tolerance_evidence,
        )
        for rule_id, evaluator in (
            (R_MGE_001, evaluate_r_mge_001),
            (R_MGE_002, evaluate_r_mge_002),
            (R_MGE_003, evaluate_r_mge_003),
        ):
            rule = authorized_rule(rule_id, context.rules_version)
            assessments_by_rule[rule_id] = evaluator(
                purchase,
                context,
                rule,
                profitability.profitability_execution,
                profitability.profitability_evidence,
                bundle,
            )

    catalog_rule_ids = implemented_rule_ids()
    executed_rule_ids = tuple(
        rule_id for rule_id in catalog_rule_ids if rule_id in assessments_by_rule
    )
    omitted_rule_ids = tuple(
        rule_id for rule_id in catalog_rule_ids if rule_id not in assessments_by_rule
    )
    ordered_assessments = tuple(
        assessments_by_rule[rule_id] for rule_id in executed_rule_ids
    )

    engine_result = run_authorized_assessments_vertical(
        purchase=purchase,
        context=context,
        assessments=ordered_assessments,
        base_result=base_result,
    )
    return DecisionRuleExecutionResult(
        executed_rule_ids=executed_rule_ids,
        omitted_rule_ids=omitted_rule_ids,
        rules_engine_result=engine_result,
    )


__all__ = [
    "DecisionRuleExecutionResult",
    "DeliveryRuleInputs",
    "FinanceCapacityRuleInputs",
    "FinanceSafetyMarginRuleInputs",
    "HistorySufficiencyRuleInputs",
    "ProfitabilityRuleInputs",
    "StockAbsorptionRuleInputs",
    "StockExcessRuleInputs",
    "run_domain_rules",
]
