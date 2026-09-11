"""One-call execution facade for the EIOS Vertical MVP.

This module composes existing authorized layers only. It does not make a
business decision, create new rule authority, or recalculate analytical
capabilities beyond the supplied domain-rule bridges.
"""
from __future__ import annotations

from eios.core.decision_twin import DecisionTwinComparison
from eios.core.execution_boundary import ExecutionOutcome
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.negotiation_intelligence import NegotiationIntelligenceResult
from eios.core.negotiation_ladder import NegotiationLadderResult
from eios.pricing.models import PriceIntelligenceResult
from eios.quality.gate import QualityTrustResult
from eios.rules.execution_adapter import build_domain_rules_c0_invoker
from eios.rules.orchestrator import (
    DeliveryRuleInputs,
    FinanceCapacityRuleInputs,
    FinanceSafetyMarginRuleInputs,
    HistorySufficiencyRuleInputs,
    StockAbsorptionRuleInputs,
    StockExcessRuleInputs,
)
from eios.rules.runtime import ConsolidatedBaseResult
from eios.tco.models import TCOResult


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
) -> ExecutionOutcome:
    """Run the supplied Vertical MVP capabilities through one stable facade.

    C0 is included only when at least one domain-rule bundle is supplied. Other
    capabilities are included only when their already-produced result is
    supplied. Missing capabilities are omitted rather than inferred.
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
    rules_invoker = None
    if rule_bundles_present:
        rules_invoker = build_domain_rules_c0_invoker(
            base_result=base_result,
            delivery=delivery,
            stock_excess=stock_excess,
            stock_absorption=stock_absorption,
            finance_capacity=finance_capacity,
            finance_safety_margin=finance_safety_margin,
            history_sufficiency=history_sufficiency,
        )

    return run_mvp_execution(
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


__all__ = ["run_vertical_mvp_support"]
