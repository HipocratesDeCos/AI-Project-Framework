"""One-call execution facade for the EIOS Vertical MVP.

This module composes existing authorized layers only. It does not make a
business decision, create new rule authority, or recalculate analytical
capabilities beyond the supplied domain-rule bridges.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence

from pydantic import BaseModel, ConfigDict

from eios.core.execution_boundary import ExecutionOutcome
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import CapabilityInvoker, run_mvp_execution
from eios.core.negotiation_intelligence import NegotiationIntelligenceResult
from eios.core.negotiation_ladder import NegotiationLadderResult
from eios.core.o2 import O2SupportPackage
from eios.core.o2_o3_integration import build_o2_support_from_o3
from eios.core.orchestration import CapabilityExecution
from eios.core.scenario_evaluation import ScenarioEvaluationResult
from eios.rules.orchestrator import (
    DecisionRuleExecutionResult,
    DeliveryRuleInputs,
    FinanceCapacityRuleInputs,
    FinanceSafetyMarginRuleInputs,
    HistorySufficiencyRuleInputs,
    StockAbsorptionRuleInputs,
    StockExcessRuleInputs,
    run_domain_rules,
)
from eios.rules.runtime import ConsolidatedBaseResult
from eios.tco.models import TCOResult


class VerticalMVPSupportResult(BaseModel):
    """Application output preserving E2E, Rules/CRC and scenario support detail."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    execution: ExecutionOutcome
    rules: DecisionRuleExecutionResult | None = None
    scenario_support: O2SupportPackage | None = None

    @property
    def status(self):
        return self.execution.status

    @property
    def capability_results(self):
        return self.execution.capability_results

    @property
    def crc_result(self):
        return None if self.rules is None else self.rules.crc_result

    @property
    def executed_rule_ids(self) -> tuple[str, ...]:
        return () if self.rules is None else self.rules.executed_rule_ids

    @property
    def omitted_rule_ids(self) -> tuple[str, ...]:
        return () if self.rules is None else self.rules.omitted_rule_ids


def _capability_snapshot_invoker(
    capability: CapabilityExecution,
) -> Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]:
    snapshot = capability.model_copy(deep=True)

    def invoke(_: PurchaseOperation, __: DecisionContext) -> CapabilityExecution:
        return snapshot.model_copy(deep=True)

    return invoke


def run_vertical_mvp_support(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    policy_version: str,
    base_result: ConsolidatedBaseResult,
    delivery: DeliveryRuleInputs | None = None,
    stock_excess: StockExcessRuleInputs | None = None,
    stock_absorption: StockAbsorptionRuleInputs | None = None,
    finance_capacity: FinanceCapacityRuleInputs | None = None,
    finance_safety_margin: FinanceSafetyMarginRuleInputs | None = None,
    history_sufficiency: HistorySufficiencyRuleInputs | None = None,
    quality_invoker: CapabilityInvoker | None = None,
    price_invoker: CapabilityInvoker | None = None,
    tco_result: TCOResult | None = None,
    decision_twin_invoker: CapabilityInvoker | None = None,
    scenario_evaluation_results: Sequence[ScenarioEvaluationResult] = (),
    negotiation_intelligence_result: NegotiationIntelligenceResult | None = None,
    negotiation_ladder_result: NegotiationLadderResult | None = None,
) -> VerticalMVPSupportResult:
    """Run supplied Vertical MVP capabilities and preserve detailed outputs.

    Rule bridges are evaluated once. QTG, PRICE and Decision Twin outputs must
    be supplied through explicit invokers rather than detached raw results.
    Scenario evaluation results are not recalculated: when supplied, they are
    coordinated through the validated O3→O2 bridge and represented as one
    SCENARIO_COORDINATION capability. Missing capabilities are omitted rather
    than inferred.
    """
    rule_bundles_present = any(
        item is not None
        for item in (
            delivery,
            stock_excess,
            stock_absorption,
            finance_capacity,
            finance_safety_margin,
            history_sufficiency,
        )
    )

    rules_result: DecisionRuleExecutionResult | None = None
    rules_invoker = None
    if rule_bundles_present:
        rules_result = run_domain_rules(
            purchase=purchase,
            context=context,
            base_result=base_result,
            delivery=delivery,
            stock_excess=stock_excess,
            stock_absorption=stock_absorption,
            finance_capacity=finance_capacity,
            finance_safety_margin=finance_safety_margin,
            history_sufficiency=history_sufficiency,
        )
        rules_invoker = _capability_snapshot_invoker(rules_result.c0_capability)

    scenario_results = tuple(scenario_evaluation_results)
    scenario_support = None
    if scenario_results:
        scenario_support = build_o2_support_from_o3(
            purchase,
            context,
            scenario_results,
        )

    execution = run_mvp_execution(
        purchase=purchase,
        context=context,
        policy_version=policy_version,
        quality_invoker=quality_invoker,
        price_invoker=price_invoker,
        rules_invoker=rules_invoker,
        tco_result=tco_result,
        decision_twin_invoker=decision_twin_invoker,
        scenario_coordination_result=scenario_support,
        negotiation_intelligence_result=negotiation_intelligence_result,
        negotiation_ladder_result=negotiation_ladder_result,
    )
    return VerticalMVPSupportResult(
        execution=execution,
        rules=rules_result,
        scenario_support=scenario_support,
    )


__all__ = ["VerticalMVPSupportResult", "run_vertical_mvp_support"]
