"""One-call execution facade for the EIOS Vertical MVP.

This module composes existing authorized layers only. It does not make a
business decision, create new rule authority, or recalculate analytical
capabilities beyond the supplied domain-rule bridges.
"""
from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel, ConfigDict

from eios.core.decision_twin import DecisionTwinComparison
from eios.core.execution_boundary import ExecutionOutcome
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.negotiation_intelligence import NegotiationIntelligenceResult
from eios.core.negotiation_ladder import NegotiationLadderResult
from eios.core.orchestration import CapabilityExecution
from eios.pricing.models import PriceIntelligenceResult
from eios.quality.gate import QualityTrustResult
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
    """Application-level output preserving E2E and Rules/CRC detail."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    execution: ExecutionOutcome
    rules: DecisionRuleExecutionResult | None = None

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
    price_result: PriceIntelligenceResult | None = None,
    tco_result: TCOResult | None = None,
    quality_result: QualityTrustResult | None = None,
    decision_twin_result: DecisionTwinComparison | None = None,
    negotiation_intelligence_result: NegotiationIntelligenceResult | None = None,
    negotiation_ladder_result: NegotiationLadderResult | None = None,
) -> VerticalMVPSupportResult:
    """Run supplied Vertical MVP capabilities and preserve detailed rule output.

    Rule bridges are evaluated once. Their C0 capability is snapshotted for the
    E2E boundary, while the complete Rules/CRC result remains available to the
    caller. Missing capabilities are omitted rather than inferred.
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

    execution = run_mvp_execution(
        purchase=purchase,
        context=context,
        policy_version=policy_version,
        rules_invoker=rules_invoker,
        price_result=price_result,
        tco_result=tco_result,
        quality_result=quality_result,
        decision_twin_result=decision_twin_result,
        negotiation_intelligence_result=negotiation_intelligence_result,
        negotiation_ladder_result=negotiation_ladder_result,
    )
    return VerticalMVPSupportResult(
        execution=execution,
        rules=rules_result,
    )


__all__ = ["VerticalMVPSupportResult", "run_vertical_mvp_support"]
